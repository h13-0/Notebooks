import argparse
import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path

from git import Repo, GitCommandError
from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.keyboard import send_keys
from pywinauto.timings import TimeoutError


NEW_NOTE_PATTERN = re.compile(r"Ctrl\s*\+\s*N", re.IGNORECASE)  # Regular expressions used to grab widget "Create new note (Ctrl+N)"
COMMAND_INPUT_PATTERN = re.compile(r"Select a command")         # The regular expression of prompt words for Ctrl+P panel widget in the current Obsidian language. 
EXPORT_BUTTON_PATTERN = re.compile(r"Export")                   # The export button regular expression in the current language.
FINISHED_TOAST_PATTERN = re.compile(r"Finished HTML Export:", re.IGNORECASE)
CANCEL_BUTTON_PATTERN = re.compile(r"Cancel", re.IGNORECASE)
COMMAND_TEXT = "Webpage HTML Export: Set html export settings"


def configure_logging(log_file: Path | None) -> logging.Logger:
    """Create a logger that always writes to stdout and optionally a file."""
    logger = logging.getLogger("exporter")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def terminate_obsidian(logger: logging.Logger) -> None:
    """Force close all Obsidian processes so the UI state is predictable."""
    logger.info("Stopping any running Obsidian processes.")
    result = subprocess.run(
        ["taskkill", "/IM", "Obsidian.exe", "/F"],
        capture_output=True,
        text=True,
        encoding="gbk",
        errors="ignore",
    )
    if result.returncode == 0:
        logger.info("Successfully terminated existing Obsidian instances.")
    else:
        stdout = (result.stdout or "").lower()
        stderr = (result.stderr or "").lower()
        no_process_tokens = ("not found", "no instance")
        if any(token in stdout or token in stderr for token in no_process_tokens):
            logger.info("No Obsidian processes were running.")
        else:
            logger.warning(
                "taskkill exited with code %s. stdout: %s stderr: %s",
                result.returncode,
                result.stdout.strip(),
                result.stderr.strip(),
            )


def checkout_branch(vault_dir: Path, branch: str, logger: logging.Logger) -> None:
    """Check out the requested git branch for the vault."""
    logger.info("Checking out branch '%s' in %s.", branch, vault_dir)
    repo = Repo(vault_dir, search_parent_directories=True)
    try:
        logger.info("Pulling latest changes from remote for %s.", branch)
        repo.git.fetch("--all")
        repo.git.pull()
        repo.git.checkout("-f", branch)
    except GitCommandError as exc:
        logger.error("Failed to checkout branch '%s': %s", branch, exc)
        raise


def remove_workspace_file(vault_dir: Path, logger: logging.Logger) -> None:
    """Delete the workspace layout file so the UI opens in a known state."""
    workspace = vault_dir / ".obsidian" / "workspace.json"
    if workspace.exists():
        logger.info("Removing workspace file %s.", workspace)
        try:
            workspace.unlink()
        except Exception as exc:
            logger.error("Failed to remove workspace file %s: %s", workspace, exc)
    else:
        logger.info("Workspace file %s does not exist; skipping removal.", workspace)


def update_export_settings(vault_dir: Path, export_path: Path, logger: logging.Logger) -> None:
    """Update the webpage-html-export plugin configuration with the desired export path."""
    config_path = vault_dir / ".obsidian" / "plugins" / "webpage-html-export" / "data.json"
    if not config_path.exists():
        logger.warning("Export plugin configuration %s does not exist; skipping update.", config_path)
        return

    try:
        with config_path.open("r", encoding="utf-8") as fh:
            config = json.load(fh)
    except Exception as exc:
        logger.error("Failed to read export configuration %s: %s", config_path, exc)
        return

    export_options = config.setdefault("exportOptions", {})
    desired_path = str(export_path)
    if export_options.get("exportPath") == desired_path:
        logger.info("Export path already set to %s; no update necessary.", desired_path)
        return

    export_options["exportPath"] = desired_path
    try:
        with config_path.open("w", encoding="utf-8") as fh:
            json.dump(config, fh, ensure_ascii=False, indent=2)
        logger.info("Updated exportPath to %s in %s.", desired_path, config_path)
    except Exception as exc:
        logger.error("Failed to write export configuration %s: %s", config_path, exc)


def launch_obsidian(obsidian_path: Path, window_title: str, logger: logging.Logger):
    """Start Obsidian and wait for the main window to become interactive."""
    logger.info("Launching Obsidian from %s.", obsidian_path)
    app = Application(backend="uia")
    app.start(cmd_line=str(obsidian_path))
    desktop = Desktop(backend="uia")
    target_pid = app.process

    def _find_window(timeout: float = 60.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            # 首先尝试在刚启动的进程内查找窗口
            try:
                candidate = app.window(title_re=window_title)
                if candidate.exists(timeout=0.1):
                    try:
                        if candidate.element_info.process_id == target_pid:
                            return candidate
                    except ElementNotFoundError:
                        pass
            except ElementNotFoundError:
                pass

            # 如果未命中，再在桌面层面筛选相同进程的窗口
            try:
                candidates = desktop.windows(title_re=window_title)
            except ElementNotFoundError:
                candidates = []

            for spec in candidates:
                pid = getattr(spec, "process", None)
                if pid is None:
                    try:
                        pid = spec.element_info.process_id
                    except Exception:
                        pid = None

                if pid == target_pid:
                    return spec

            time.sleep(0.5)

        raise TimeoutError(f"在超时时间内未找到进程 ID {target_pid} 对应的窗口。")

    try:
        window_spec = _find_window()
        window_spec.wait("visible enabled ready", timeout=60)
        window_spec.set_focus()
        logger.info("Obsidian window is ready and focused.")
        return window_spec, desktop
    except ElementNotFoundError as exc:
        logger.error("Could not find Obsidian window matching '%s'.", window_title)
        raise TimeoutError(str(exc)) from exc


def _iter_controls(root):
    """Safely iterate UIA descendants for the given wrapper."""
    try:
        return root.descendants()
    except Exception:
        return []


def wait_for_control(
    roots,
    *,
    name_pattern: re.Pattern[str],
    control_type: str | None,
    timeout: float,
    retry_interval: float = 0.5,
):
    """Poll UIA for a control matching the pattern until timeout."""
    if not isinstance(roots, (list, tuple)):
        roots = [roots]
    deadline = time.time() + timeout
    while time.time() < deadline:
        for root in roots:
            for ctrl in _iter_controls(root):
                name = ctrl.element_info.name or ""
                if not name_pattern.search(name):
                    continue
                if control_type and ctrl.friendly_class_name().lower() != control_type.lower():
                    continue
                return ctrl
        time.sleep(retry_interval)
    raise TimeoutError(
        f"Timed out waiting for control matching '{name_pattern.pattern}' "
        f"with type '{control_type}'."
    )


def wait_for_disappearance(
    roots,
    *,
    name_pattern: re.Pattern[str],
    control_type: str | None,
    timeout: float,
    retry_interval: float = 0.5,
):
    """Wait until a previously visible control is no longer found."""
    if not isinstance(roots, (list, tuple)):
        roots = [roots]
    deadline = time.time() + timeout
    while time.time() < deadline:
        found = False
        for root in roots:
            for ctrl in _iter_controls(root):
                name = ctrl.element_info.name or ""
                if not name_pattern.search(name):
                    continue
                if control_type and ctrl.friendly_class_name().lower() != control_type.lower():
                    continue
                found = True
                break
            if found:
                break
        if not found:
            return
        time.sleep(retry_interval)
    raise TimeoutError(
        f"Control matching '{name_pattern.pattern}' with type '{control_type}' did not disappear in time."
    )


def sample_controls(root, substring: str, limit: int = 10) -> list[str]:
    """Collect a short list of controls whose names contain the substring."""
    samples: list[str] = []
    for ctrl in _iter_controls(root):
        name = (ctrl.element_info.name or "").strip()
        if substring in name:
            samples.append(f"{ctrl.friendly_class_name()}:{name}")
            if len(samples) >= limit:
                break
    return samples


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the exporter automation."""
    parser = argparse.ArgumentParser(description="Automate Obsidian HTML export.")
    parser.add_argument(
        "--vault-dir",
        required=True,
        type=Path,
        help="Path to the Obsidian vault directory (git repository).",
    )
    parser.add_argument(
        "--export-path",
        required=True,
        type=Path,
        help="Target directory for the Webpage HTML Export plugin output.",
    )
    parser.add_argument(
        "--obsidian-path",
        required=True,
        type=Path,
        help="Path to Obsidian.exe.",
    )
    parser.add_argument(
        "--window-title",
        default=r".*Obsidian.*",
        help="Regular expression for the Obsidian window title.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Optional log file path.",
    )
    parser.add_argument(
        "--git-branch",
        default="master",
        help="Git branch to checkout before exporting.",
    )
    return parser.parse_args()


def ensure_environment(logger: logging.Logger) -> None:
    """Sanity-check required Python modules are importable."""
    required = {"pywinauto", "git"}
    for module in required:
        logger.debug("Verified dependency: %s", module)


def main() -> int:
    """Drive the Obsidian export workflow end-to-end."""
    args = parse_args()
    logger = configure_logging(args.log_file)

    try:
        # Preparation: ensure dependencies are present and any running instance is closed.
        ensure_environment(logger)
        terminate_obsidian(logger)
        checkout_branch(args.vault_dir, args.git_branch, logger)
        export_path = args.export_path.expanduser()
        try:
            export_path = export_path.resolve(strict=False)
        except TypeError:
            export_path = export_path.resolve()
        update_export_settings(args.vault_dir, export_path, logger)
        remove_workspace_file(args.vault_dir, logger)
        window, desktop = launch_obsidian(args.obsidian_path, args.window_title, logger)

        # Wait for the main workspace to finish loading.
        logger.info("Waiting for indicator containing '%s'.", "Create new note (Ctrl + N)")
        try:
            wait_for_control(
                [window, desktop],
                name_pattern=NEW_NOTE_PATTERN,
                control_type=None,
                timeout=60,
            )
        except TimeoutError:
            samples = sample_controls(desktop, "Ctrl", limit=10)
            logger.error(
                "No widget containing 'Ctrl + N' prompt detected within 60 seconds, sample: %s",
                samples,
            )
            return 1

        # Step 2: open the command palette.
        logger.info("Opening command palette with Ctrl+P.")
        window.set_focus()
        send_keys("^p")

        # Step 3: focus the palette input and submit the export command.
        logger.info("Waiting for command input box.")
        try:
            command_edit = wait_for_control(
                [window, desktop],
                name_pattern=COMMAND_INPUT_PATTERN,
                control_type="edit",
                timeout=30,
            )
        except TimeoutError:
            samples = sample_controls(desktop, "command", limit=10)
            logger.error(
                "The command palette input did not appear within 30 seconds. Samples: %s",
                samples,
            )
            return 1

        logger.info("Typing command '%s'.", COMMAND_TEXT)
        try:
            command_edit.click_input()
            command_edit.type_keys("^a{BACKSPACE}", pause=0.05, set_foreground=True)
            command_edit.type_keys(
                COMMAND_TEXT,
                with_spaces=True,
                pause=0.05,
                set_foreground=True,
            )
            command_edit.type_keys("{ENTER}", pause=0.05, set_foreground=True)
        except Exception as exc:
            logger.error("Failed to send command text: %s", exc)
            return 1

        # Step 4: wait for the export dialog and trigger the export.
        logger.info("Waiting for 'Export' button.")
        try:
            export_button = wait_for_control(
                [window, desktop],
                name_pattern=EXPORT_BUTTON_PATTERN,
                control_type="button",
                timeout=60,
            )
        except TimeoutError:
            samples = sample_controls(desktop, "Export", limit=10)
            logger.error(
                "An 'Export' button did not appear within 60 seconds. Samples: %s",
                samples,
            )
            return 1

        logger.info("Clicking 'Export' button.")
        try:
            export_button.click_input()
        except Exception as exc:
            logger.error("Failed to click the 'Export' button: %s", exc)
            return 1

        logger.info("Waiting for 'Finished HTML Export:' notification.")
        try:
            wait_for_control(
                [window, desktop],
                name_pattern=FINISHED_TOAST_PATTERN,
                control_type=None,
                timeout=1800,
            )
        except TimeoutError:
            logger.error(
                "No notification starting with 'Finished HTML Export:' appeared within 120 seconds."
            )
            return 1

        logger.info("Export completed successfully.")
        return 0
    except (TimeoutError, ElementNotFoundError, GitCommandError) as exc:
        logger.error("Automation failed: %s", exc)
    except Exception:
        logger.exception("Unexpected error during automation.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
