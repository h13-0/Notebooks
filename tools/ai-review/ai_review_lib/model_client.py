from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


class ModelClientError(RuntimeError):
    pass


def endpoint_for_provider(provider: str, secrets: dict[str, Any]) -> tuple[str, str]:
    item = (secrets.get("providers") or {}).get(provider) or {}
    base_url = str(item.get("base_url") or "").rstrip("/")
    api_key = str(item.get("api_key") or "")
    if not base_url or not api_key or api_key == "YOUR_API_KEY":
        raise ModelClientError(f"provider `{provider}` 缺少 base_url/api_key")
    if not base_url.endswith("/chat/completions"):
        base_url = base_url.rstrip("/") + "/chat/completions"
    return base_url, api_key


def _parse_non_stream_response(data: dict[str, Any]) -> str:
    return data.get("choices", [{}])[0].get("message", {}).get("content", "")


def _parse_stream_response(resp: Any, max_total_seconds: int | None = None) -> str:
    """Parse OpenAI-compatible SSE chunks.

    中文说明：开启 stream 后，timeout 变成 socket 空闲超时。只要服务端持续
    输出 chunk，`readline()` 就会持续返回，不会因为总生成时间长而被误判为无响应。
    """
    pieces: list[str] = []
    started = time.monotonic()
    for raw_line in resp:
        if max_total_seconds and time.monotonic() - started > max_total_seconds:
            raise ModelClientError(f"stream total timeout after {max_total_seconds}s")
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line or not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            break
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            continue
        choice = (data.get("choices") or [{}])[0]
        delta = choice.get("delta") or {}
        message = choice.get("message") or {}
        content = delta.get("content") or message.get("content") or ""
        if content:
            pieces.append(content)
    return "".join(pieces)


def call_model(
    model: dict[str, Any],
    secrets: dict[str, Any],
    prompt: str,
    timeout: int,
    stream: bool = False,
    stream_total_timeout: int | None = None,
) -> dict[str, Any]:
    """Call one OpenAI-compatible chat completion endpoint.

    中文说明：外部 voter 统一走 OpenAI-compatible chat/completions。
    这里不吞异常，让上层按 warn-once 和 retry 策略处理。
    """
    provider = str(model.get("provider") or "")
    url, api_key = endpoint_for_provider(provider, secrets)
    generation = model.get("generation") or {}
    payload = {
        "model": model.get("model") or model.get("id"),
        "messages": [
            {"role": "system", "content": "你是严格输出 JSON 的 AI Review 投票模型。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": generation.get("temperature", 0.1),
        "max_tokens": generation.get("max_tokens", 4096),
        "response_format": {"type": "json_object"},
    }
    if stream:
        payload["stream"] = True
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if stream:
                content = _parse_stream_response(resp, max_total_seconds=stream_total_timeout)
                data = None
            else:
                data = json.loads(resp.read().decode("utf-8"))
                content = _parse_non_stream_response(data)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise ModelClientError(f"HTTP {exc.code}: {body}") from exc
    if not content:
        raise ModelClientError("模型返回为空")
    content = content.strip()
    if content.startswith("```"):
        import re

        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    return json.loads(content)


def call_model_with_retry(
    model: dict[str, Any],
    secrets: dict[str, Any],
    prompt: str,
    timeout: int,
    retry: int,
    stream: bool = False,
    stream_total_timeout: int | None = None,
) -> dict[str, Any]:
    last_exc: Exception | None = None
    for attempt in range(retry + 1):
        try:
            return call_model(model, secrets, prompt, timeout, stream=stream, stream_total_timeout=stream_total_timeout)
        except Exception as exc:
            last_exc = exc
            if attempt < retry:
                time.sleep(min(2 ** attempt, 8))
    assert last_exc is not None
    raise last_exc
