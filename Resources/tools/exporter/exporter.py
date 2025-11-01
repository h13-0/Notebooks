import argparse
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


NEW_NOTE_PATTERN = re.compile(r"Ctrl\s*\+\s*N", re.IGNORECASE)
COMMAND_INPUT_PATTERN = re.compile(r"输入命令")
EXPORT_BUTTON_PATTERN = re.compile(r"导出")
FINISHED_TOAST_PATTERN = re.compile(r"Finished HTML Export:", re.IGNORECASE)
CANCEL_BUTTON_PATTERN = re.compile(r"Cancel", re.IGNORECASE)
COMMAND_TEXT = "Webpage HTML Export: Set html export settings"


def configure_logging(log_file: Path | None) -> logging.Logger:
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
        no_process_tokens = ("not found", "no instance", "未找到", "不存在")
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
    logger.info("Checking out branch '%s' in %s.", branch, vault_dir)
    repo = Repo(vault_dir, search_parent_directories=True)
    try:
        repo.git.checkout(branch)
    except GitCommandError as exc:
        logger.error("Failed to checkout branch '%s': %s", branch, exc)
        raise


def remove_workspace_file(vault_dir: Path, logger: logging.Logger) -> None:
    workspace = vault_dir / ".obsidian" / "workspace.json"
    if workspace.exists():
        logger.info("Removing workspace file %s.", workspace)
        workspace.unlink()
    else:
        logger.info("Workspace file %s does not exist; skipping removal.", workspace)


def launch_obsidian(obsidian_path: Path, window_title: str, logger: logging.Logger):
    logger.info("Launching Obsidian from %s.", obsidian_path)
    app = Application(backend="uia")
    app.start(cmd_line=str(obsidian_path))
    desktop = Desktop(backend="uia")
    try:
        window = desktop.window(title_re=window_title)
        window.wait("visible enabled ready", timeout=60)
        window.set_focus()
        logger.info("Obsidian window is ready and focused.")
        return window, desktop
    except ElementNotFoundError as exc:
        logger.error("Could not find Obsidian window matching '%s'.", window_title)
        raise TimeoutError(str(exc)) from exc


def _iter_controls(root):
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
    samples: list[str] = []
    for ctrl in _iter_controls(root):
        name = (ctrl.element_info.name or "").strip()
        if substring in name:
            samples.append(f"{ctrl.friendly_class_name()}:{name}")
            if len(samples) >= limit:
                break
    return samples


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automate Obsidian HTML export.")
    parser.add_argument(
        "--vault-dir",
        required=True,
        type=Path,
        help="Path to the Obsidian vault directory (git repository).",
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
    required = {"pywinauto", "git"}
    for module in required:
        logger.debug("Verified dependency: %s", module)


def main() -> int:
    args = parse_args()
    logger = configure_logging(args.log_file)

    try:
        ensure_environment(logger)
        terminate_obsidian(logger)
        checkout_branch(args.vault_dir, args.git_branch, logger)
        remove_workspace_file(args.vault_dir, logger)
        window, desktop = launch_obsidian(args.obsidian_path, args.window_title, logger)

        logger.info("Waiting for indicator containing '%s'.", "创建新文件 (Ctrl + N)")
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
                "在60秒内未检测到包含 'Ctrl + N' 提示的控件。样例: %s",
                samples,
            )
            return 1

        logger.info("Opening command palette with Ctrl+P.")
        window.set_focus()
        send_keys("^p")

        logger.info("Waiting for command input box.")
        try:
            command_edit = wait_for_control(
                [window, desktop],
                name_pattern=COMMAND_INPUT_PATTERN,
                control_type="edit",
                timeout=30,
            )
        except TimeoutError:
            samples = sample_controls(desktop, "命令", limit=10)
            logger.error("在30秒内未检测到 '输入命令…' 控件。样例: %s", samples)
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

        logger.info("Waiting for '导出' button.")
        try:
            export_button = wait_for_control(
                [window, desktop],
                name_pattern=EXPORT_BUTTON_PATTERN,
                control_type="button",
                timeout=60,
            )
        except TimeoutError:
            samples = sample_controls(desktop, "导出", limit=10)
            logger.error("在60秒内未检测到包含 '导出' 的按钮。样例: %s", samples)
            return 1

        logger.info("Clicking '导出' button.")
        try:
            export_button.click_input()
        except Exception as exc:
            logger.error("点击 '导出' 按钮失败: %s", exc)
            return 1

        logger.info("Waiting for 'Cancel' button to disappear.")
        try:
            wait_for_disappearance(
                [window, desktop],
                name_pattern=CANCEL_BUTTON_PATTERN,
                control_type="button",
                timeout=120,
            )
        except TimeoutError:
            logger.error("在120秒内未检测到 'Cancel' 按钮消失，退出。")
            return 1

        logger.info("Waiting for 'Finished HTML Export:' notification.")
        try:
            wait_for_control(
                [window, desktop],
                name_pattern=FINISHED_TOAST_PATTERN,
                control_type=None,
                timeout=120,
            )
        except TimeoutError:
            logger.error("在120秒内未检测到以 'Finished HTML Export:' 开头的提示，退出。")
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
