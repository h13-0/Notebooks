#!/usr/bin/env python3
"""Python build and deployment workflow driven by YAML configuration."""

from __future__ import annotations

import argparse
import logging
import posixpath
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List
import zipfile

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover - dependency check
    raise SystemExit(
        "缺少 PyYAML 依赖，请先执行 `pip install pyyaml` 再运行 build.py。"
    ) from exc


LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用 Python 执行构建与部署流程")
    parser.add_argument(
        "--config",
        default="build_config.yaml",
        help="配置文件路径（YAML 格式），默认 build_config.yaml",
    )
    parser.add_argument(
        "--remote-user",
        required=True,
        help="远程服务器用户名",
    )
    parser.add_argument(
        "--remote-password",
        required=True,
        help="远程服务器密码",
    )
    parser.add_argument(
        "--remote-host",
        required=True,
        help="远程服务器地址",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="日志级别（默认 INFO）",
    )
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
    except KeyError as exc:
        missing = exc.args[0]
        raise KeyError(f"格式化字符串缺少变量 '{missing}': {value}") from exc


def resolve_to_path(
    value: str,
    *,
    base_dir: Path,
    context: Dict[str, Any],
) -> Path:
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


def run_python_script(script_path: Path, arguments: List[str], logger: logging.Logger) -> None:
    if not script_path.exists():
        raise FileNotFoundError(f"未找到脚本: {script_path}")

    logger.info("运行脚本: %s %s", script_path, " ".join(arguments))
    cmd = [sys.executable, str(script_path), *arguments]
    completed = subprocess.run(cmd, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"脚本执行失败，退出码 {completed.returncode}: {script_path}")


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
        not_found_tokens = ("not found", "no instance", "no process found", "non-zero pkill")
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


def create_zip_archive(source: Path, archive: Path, logger: logging.Logger) -> None:
    if not source.exists():
        raise FileNotFoundError(f"待打包路径不存在: {source}")

    archive.parent.mkdir(parents=True, exist_ok=True)
    if archive.exists():
        logger.debug("移除已存在的压缩包: %s", archive)
        archive.unlink()

    logger.info("打包 %s -> %s", source, archive)

    with zipfile.ZipFile(
        archive,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:
        if source.is_dir():
            for file_path in source.rglob("*"):
                if file_path.is_file():
                    zf.write(file_path, arcname=file_path.relative_to(source))
        elif source.is_file():
            zf.write(source, arcname=source.name)
        else:
            raise FileNotFoundError(f"无法打包的路径类型: {source}")


def ensure_paramiko() -> Any:
    try:
        import paramiko  # type: ignore
    except ImportError as exc:  # pragma: no cover - dependency check
        raise SystemExit(
            "缺少 Paramiko 依赖，请执行 `pip install paramiko` 以启用远程部署功能。"
        ) from exc
    return paramiko


def run_remote_command(
    client: Any,
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


def upload_and_deploy(
    archive_path: Path,
    remote_zip_path: str,
    remote_deploy_path: str,
    *,
    host: str,
    port: int,
    username: str,
    password: str,
    logger: logging.Logger,
) -> None:
    paramiko = ensure_paramiko()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    logger.info("连接远程服务器 %s:%s", host, port)
    client.connect(hostname=host, port=port, username=username, password=password)

    try:
        remote_dir = posixpath.dirname(remote_zip_path)
        if remote_dir:
            run_remote_command(
                client,
                command=f"bash -lc {shlex.quote(f'mkdir -p {shlex.quote(remote_dir)}')}",
                logger=logger,
            )

        logger.info("上传压缩包到远程: %s", remote_zip_path)
        with client.open_sftp() as sftp:
            sftp.put(str(archive_path), remote_zip_path)

        script_lines = [
            "set -euo pipefail",
            f"zip_path={shlex.quote(remote_zip_path)}",
            f"target_dir={shlex.quote(remote_deploy_path)}",
            'tmp_dir="${target_dir}_new"',
            'mkdir -p "$(dirname "$target_dir")"',
            'rm -rf "$tmp_dir"',
            'mkdir -p "$tmp_dir"',
            'unzip -o "$zip_path" -d "$tmp_dir"',
            'rm -rf "$target_dir"',
            'mv "$tmp_dir" "$target_dir"',
        ]
        script = "\n".join(script_lines) + "\n"

        logger.info("远程解压并覆盖部署: %s", remote_deploy_path)
        run_remote_command(
            client,
            command="bash -s",
            stdin_data=script,
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
        exporter_path = resolve_to_path(
            exporter_cfg["path"],
            base_dir=config_dir,
            context=context,
        )
        exporter_args = resolve_arguments(
            exporter_cfg.get("args", []),
            context=context,
        )
        run_python_script(exporter_path, exporter_args, logger)
        process_to_terminate = exporter_cfg.get("terminate_process")
        if process_to_terminate:
            terminate_process(format_string(process_to_terminate, context), logger)

    statistics_cfg = scripts_cfg.get("statistics")
    if statistics_cfg:
        statistics_path = resolve_to_path(
            statistics_cfg["path"],
            base_dir=config_dir,
            context=context,
        )
        statistics_args = resolve_arguments(
            statistics_cfg.get("args", []),
            context=context,
        )
        run_python_script(statistics_path, statistics_args, logger)

    package_cfg = config.get("package")
    if not package_cfg:
        raise KeyError("配置文件缺少 package 节点")

    package_source = resolve_to_path(
        package_cfg["source"],
        base_dir=config_dir,
        context=context,
    )
    archive_path = resolve_to_path(
        package_cfg["archive"],
        base_dir=config_dir,
        context=context,
    )

    create_zip_archive(package_source, archive_path, logger)

    remote_cfg = config.get("remote")
    if not remote_cfg:
        raise KeyError("配置文件缺少 remote 节点")

    remote_zip_path = format_string(remote_cfg["zip_path"], context)
    remote_deploy_path = format_string(remote_cfg["deploy_path"], context)
    remote_port = int(remote_cfg.get("port", 22))

    upload_and_deploy(
        archive_path=archive_path,
        remote_zip_path=remote_zip_path,
        remote_deploy_path=remote_deploy_path,
        host=args.remote_host,
        port=remote_port,
        username=args.remote_user,
        password=args.remote_password,
        logger=logger,
    )

    logger.info("全部流程执行完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
