#!/usr/bin/env python3
"""Python build and deployment workflow driven by YAML configuration."""

from __future__ import annotations

import argparse
import logging
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover - dependency check
    raise SystemExit("缺少 PyYAML 依赖，请先执行 `pip install pyyaml` 再运行 build.py。") from exc


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DEFAULT_RSYNC_OPTIONS = ["-az", "--delete"]
DEFAULT_DEPLOY_OPTIONS = ["-a", "--delete"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用 Python 执行构建与部署流程")
    parser.add_argument(
        "--config",
        default="build_config.yaml",
        help="配置文件路径（YAML 格式），默认 build_config.yaml",
    )
    parser.add_argument("--remote-user", required=True, help="远程服务器用户名")
    parser.add_argument("--remote-password", required=True, help="远程服务器密码")
    parser.add_argument("--remote-host", required=True, help="远程服务器地址")
    parser.add_argument("--log-level", default="INFO", help="日志级别（默认 INFO）")
    return parser.parse_args()


def configure_logging(level: str) -> logging.Logger:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=numeric_level, format=LOG_FORMAT)
    return logging.getLogger("build")


def load_config(path: Path, logger: logging.Logger) -> Dict[str, Any]:
    logger.debug("读取配置文件 %s", path)
    if not path.exists():
        raise FileNotFoundError(f"未找到配置文件: {path}")
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def format_string(value: str, context: Dict[str, Any]) -> str:
    try:
        return value.format_map(context)
    except ValueError:
        # 忽略位置占位符等格式化错误，直接返回原文本
        return value
    except KeyError as exc:
        missing = exc.args[0]
        raise KeyError(f"格式化字符串缺少变量 '{missing}': {value}") from exc


def resolve_to_path(value: str, *, base_dir: Path, context: Dict[str, Any]) -> Path:
    formatted = format_string(value, context)
    candidate = Path(formatted)
    if not candidate.is_absolute():
        candidate = (base_dir / candidate).resolve()
    return candidate


def resolve_arguments(values: Iterable[Any], context: Dict[str, Any]) -> List[str]:
    result: List[str] = []
    for item in values:
        if isinstance(item, str):
            result.append(format_string(item, context))
        else:
            result.append(str(item))
    return result


def format_local_path_for_rsync(path: Path) -> str:
    """Convert local filesystem path to rsync-friendly string, especially for Windows."""
    resolved = path.resolve()
    posix_path = resolved.as_posix()
    if not sys.platform.startswith("win"):
        return posix_path

    drive = resolved.drive
    if drive and len(drive) == 2 and drive[1] == ":":
        # Convert drive letter path to /cygdrive/<drive> style for Cygwin/MSYS rsync
        suffix = posix_path[2:] if len(posix_path) > 2 else ""
        return f"/cygdrive/{drive[0].lower()}{suffix}"

    return posix_path


def run_python_script(script_path: Path, arguments: List[str], logger: logging.Logger) -> None:
    if not script_path.exists():
        raise FileNotFoundError(f"未找到脚本: {script_path}")

    logger.info("运行脚本: %s %s", script_path, " ".join(arguments))
    cmd = [sys.executable, str(script_path), *arguments]
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"脚本执行失败，退出码 {completed.returncode}: {script_path}")


def run_docker_export(
    docker_cfg: Dict[str, Any],
    *,
    base_dir: Path,
    context: Dict[str, Any],
    logger: logging.Logger,
) -> None:
    docker_path = find_executable(["docker"])
    image = format_string(docker_cfg["image"], context)
    vault_dir = resolve_to_path(docker_cfg["vault_dir"], base_dir=base_dir, context=context)
    output_dir = resolve_to_path(docker_cfg["output_dir"], base_dir=base_dir, context=context)
    git_branch = format_string(docker_cfg.get("git_branch", ""), context).strip()

    env_cfg = docker_cfg.get("env", {})
    env_args: List[str] = []
    for key, value in env_cfg.items():
        env_args.extend(["-e", f"{key}={format_string(str(value), context)}"])

    vault_mount = f"{vault_dir.as_posix()}:/vault"
    output_mount = f"{output_dir.as_posix()}:/output"

    git_path = find_executable(["git"])
    pull_cmd = [git_path, "-C", str(vault_dir), "pull", "--recurse-submodules"]
    if git_branch:
        pull_cmd.extend(["origin", git_branch])

    logger.info("拉取 vault_dir 最新版本: %s", " ".join(pull_cmd))
    completed = subprocess.run(pull_cmd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"拉取 vault_dir 失败，退出码 {completed.returncode}: {vault_dir}")

    submodule_cmd = [git_path, "-C", str(vault_dir), "submodule", "update", "--init", "--recursive"]
    logger.info("更新 vault_dir 子模块: %s", " ".join(submodule_cmd))
    completed = subprocess.run(submodule_cmd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"更新 vault_dir 子模块失败，退出码 {completed.returncode}: {vault_dir}")

    run_cmd = [
        docker_path,
        "run",
        "--rm",
        *env_args,
        "-v",
        vault_mount,
        "-v",
        output_mount,
        image,
    ]
    logger.info("运行 Docker 导出: %s", " ".join(run_cmd))
    completed = subprocess.run(run_cmd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"Docker 导出失败，退出码 {completed.returncode}: {image}")


def terminate_process(process_name: str, logger: logging.Logger) -> None:
    """Attempt to terminate a process; ignore if it is not running."""
    if not process_name:
        return

    logger.info("尝试关闭进程: %s", process_name)
    if sys.platform.startswith("win"):
        cmd = ["taskkill", "/IM", process_name, "/F"]
    else:
        cmd = ["pkill", "-f", process_name]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        check=False,
    )

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    if result.returncode == 0:
        logger.info("进程 %s 已关闭。", process_name)
    else:
        combined = f"{stdout} {stderr}".lower()
        not_found_tokens = ("not found", "no instance", "no process found", "no task running")
        if any(token in combined for token in not_found_tokens) or result.returncode in {1, 128}:
            logger.info("进程 %s 未在运行。", process_name)
        else:
            logger.warning(
                "尝试关闭进程 %s 时出现非致命错误 (exit %s): stdout=%s stderr=%s",
                process_name,
                result.returncode,
                stdout,
                stderr,
            )


def find_executable(candidates: Iterable[str]) -> str:
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    raise FileNotFoundError(f"无法找到可执行文件: {', '.join(candidates)}")


def run_rsync_with_retry(
    source: Path,
    remote_path: str,
    *,
    host: str,
    port: int,
    username: str,
    password: str,
    options: List[str],
    ssh_options: List[str],
    retries: int,
    logger: logging.Logger,
) -> None:
    rsync_path = find_executable(["rsync"])
    sshpass_path = shutil.which("sshpass")
    plink_path = shutil.which("plink")

    use_sshpass = bool(password and sshpass_path)
    use_plink = bool(password and not use_sshpass and plink_path)

    if password and not (use_sshpass or use_plink):
        logger.warning("未找到 sshpass 或 plink，将尝试使用交互式密码或现有 SSH 配置。")

    source = source.resolve()
    source_arg = format_local_path_for_rsync(source)
    if source.is_dir() and not source_arg.endswith("/"):
        source_arg += "/"

    remote_dir = remote_path.rstrip("/") + "/"
    remote_arg = f"{username}@{host}:{remote_dir}"

    if use_plink:
        ssh_parts = [plink_path, "-ssh", "-batch"]
        ssh_parts_masked = [plink_path, "-ssh", "-batch"]
        if port:
            ssh_parts += ["-P", str(port)]
            ssh_parts_masked += ["-P", str(port)]
        ssh_parts += ["-pw", password]
        ssh_parts_masked += ["-pw", "******"]
        ssh_parts.extend(ssh_options)
        ssh_parts_masked.extend(ssh_options)
    else:
        ssh_parts = ["ssh"]
        ssh_parts_masked = ["ssh"]
        if port:
            ssh_parts += ["-p", str(port)]
            ssh_parts_masked += ["-p", str(port)]
        ssh_parts.extend(ssh_options)
        ssh_parts_masked.extend(ssh_options)

    ssh_cmd = shlex.join(ssh_parts)
    ssh_cmd_masked = shlex.join(ssh_parts_masked)

    base_cmd = [rsync_path, *options, "-e", ssh_cmd, source_arg, remote_arg]
    log_cmd = [rsync_path, *options, "-e", ssh_cmd_masked, source_arg, remote_arg]

    if use_sshpass:
        base_cmd = [sshpass_path, "-p", password, *base_cmd]
        log_cmd = [sshpass_path, "-p", "******", *log_cmd]

    logger.info("启动 rsync 同步: %s", " ".join(log_cmd))
    logger.debug("rsync 命令参数: %s", base_cmd)

    for attempt in range(1, max(1, retries) + 1):
        cmd = base_cmd
        if sshpass_path and password:
            cmd = [sshpass_path, "-p", password, *base_cmd]

        logger.info("rsync 同步尝试 %d/%d", attempt, max(1, retries))
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=False,
        )

        if completed.returncode == 0:
            logger.info("rsync 同步完成。")
            return

        logger.warning(
            "rsync 失败 (exit %s)，stdout: %s stderr: %s",
            completed.returncode,
            (completed.stdout or "").strip(),
            (completed.stderr or "").strip(),
        )
        if attempt < retries:
            time.sleep(3)

    raise RuntimeError("rsync 重试多次后仍未成功完成同步。")


def ensure_paramiko():
    try:
        import paramiko  # type: ignore
    except ImportError as exc:  # pragma: no cover - dependency check
        raise SystemExit("缺少 Paramiko 依赖，请执行 `pip install paramiko`。") from exc
    return paramiko


def run_remote_command(
    client,
    command: str,
    *,
    stdin_data: str | None = None,
    logger: logging.Logger,
) -> None:
    logger.debug("执行远程命令: %s", command)
    stdin, stdout, stderr = client.exec_command(command)
    if stdin_data:
        stdin.write(stdin_data)
        stdin.flush()
    stdin.close()

    exit_status = stdout.channel.recv_exit_status()
    out_text = stdout.read().decode("utf-8", errors="ignore").strip()
    err_text = stderr.read().decode("utf-8", errors="ignore").strip()

    if out_text:
        logger.debug("远程 stdout: %s", out_text)
    if err_text:
        logger.debug("远程 stderr: %s", err_text)

    if exit_status != 0:
        raise RuntimeError(
            f"远程命令执行失败 (exit {exit_status}): {command}\nstdout: {out_text}\nstderr: {err_text}"
        )


def deploy_from_remote(
    remote_source: str,
    remote_target: str,
    options: List[str],
    *,
    host: str,
    port: int,
    username: str,
    password: str,
    logger: logging.Logger,
    post_commands: Optional[List[str]] = None,
) -> None:
    paramiko = ensure_paramiko()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    logger.info("连接远程服务器以部署: %s:%s", host, port)
    client.connect(hostname=host, port=port, username=username, password=password)

    try:
        target_norm = remote_target.rstrip("/")
        source_norm = remote_source.rstrip("/") + "/"
        run_remote_command(
            client,
            command=f"bash -lc {shlex.quote(f'mkdir -p {shlex.quote(target_norm)}')}",
            logger=logger,
        )

        option_str = " ".join(shlex.quote(opt) for opt in options)
        rsync_cmd = "rsync"
        if option_str:
            rsync_cmd += f" {option_str}"
        rsync_cmd += f" {shlex.quote(source_norm)} {shlex.quote(target_norm + '/')}"

        logger.info("远程部署命令: %s", rsync_cmd)
        run_remote_command(
            client,
            command=f"bash -lc {shlex.quote(rsync_cmd)}",
            logger=logger,
        )

        if post_commands:
            logger.info("执行部署后命令...")
            for command in post_commands:
                if not command:
                    continue
                logger.info("远程执行: %s", command)
                run_remote_command(
                    client,
                    command=f"bash -lc {shlex.quote(command)}",
                    logger=logger,
                )
    finally:
        client.close()


def main() -> int:
    args = parse_args()
    logger = configure_logging(args.log_level)
    script_root = Path(__file__).resolve().parent

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (script_root / config_path).resolve()

    config = load_config(config_path, logger)
    config_dir = config_path.parent

    context: Dict[str, Any] = dict(config.get("variables", {}))
    context.setdefault("project_root", str(script_root))
    context.setdefault("config_dir", str(config_dir))

    scripts_cfg = config.get("scripts", {})

    exporter_cfg = scripts_cfg.get("exporter")
    if exporter_cfg:
        docker_cfg = exporter_cfg.get("docker")
        if docker_cfg:
            run_docker_export(docker_cfg, base_dir=config_dir, context=context, logger=logger)

    statistics_cfg = scripts_cfg.get("statistics")
    if statistics_cfg:
        statistics_path = resolve_to_path(statistics_cfg["path"], base_dir=config_dir, context=context)
        statistics_args = resolve_arguments(statistics_cfg.get("args", []), context=context)
        run_python_script(statistics_path, statistics_args, logger)

    remote_cfg = config.get("remote", {})
    remote_port = int(remote_cfg.get("port", 22))
    context.setdefault("remote_port", str(remote_port))

    sync_cfg = config.get("sync")
    if not sync_cfg:
        raise KeyError("配置文件缺少 sync 节点")

    sync_source = resolve_to_path(sync_cfg["source"], base_dir=config_dir, context=context)
    remote_sync_path = format_string(sync_cfg["remote_path"], context)
    context.setdefault("remote_sync_path", remote_sync_path)

    sync_options = resolve_arguments(sync_cfg.get("options", DEFAULT_RSYNC_OPTIONS), context=context)
    ssh_options = resolve_arguments(sync_cfg.get("ssh_options", []), context=context)
    retries = int(sync_cfg.get("retries", 3))

    run_rsync_with_retry(
        source=sync_source,
        remote_path=remote_sync_path,
        host=args.remote_host,
        port=remote_port,
        username=args.remote_user,
        password=args.remote_password,
        options=sync_options,
        ssh_options=ssh_options,
        retries=retries,
        logger=logger,
    )

    deploy_cfg = config.get("deploy")
    if not deploy_cfg:
        raise KeyError("配置文件缺少 deploy 节点")

    deploy_source = format_string(deploy_cfg.get("source", "{remote_sync_path}"), context)
    deploy_target = format_string(deploy_cfg["deploy_path"], context)
    deploy_options = resolve_arguments(
        deploy_cfg.get("options", DEFAULT_DEPLOY_OPTIONS),
        context=context,
    )

    raw_post_commands = context.get("post_deploy_commands", [])
    if raw_post_commands is None:
        raw_post_commands = []
    elif isinstance(raw_post_commands, str):
        raw_post_commands = [raw_post_commands]
    elif not isinstance(raw_post_commands, list):
        raw_post_commands = list(raw_post_commands)

    post_commands: List[str] = []
    for command in raw_post_commands:
        if not command:
            continue
        if not isinstance(command, str):
            command = str(command)
        post_commands.append(format_string(command, context))

    deploy_from_remote(
        remote_source=deploy_source,
        remote_target=deploy_target,
        options=deploy_options,
        host=args.remote_host,
        port=remote_port,
        username=args.remote_user,
        password=args.remote_password,
        logger=logger,
        post_commands=post_commands,
    )

    logger.info("全部流程执行完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
