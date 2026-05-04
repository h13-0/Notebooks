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


def call_model(model: dict[str, Any], secrets: dict[str, Any], prompt: str, timeout: int) -> dict[str, Any]:
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
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise ModelClientError(f"HTTP {exc.code}: {body}") from exc
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not content:
        raise ModelClientError("模型返回为空")
    content = content.strip()
    if content.startswith("```"):
        import re

        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    return json.loads(content)


def call_model_with_retry(model: dict[str, Any], secrets: dict[str, Any], prompt: str, timeout: int, retry: int) -> dict[str, Any]:
    last_exc: Exception | None = None
    for attempt in range(retry + 1):
        try:
            return call_model(model, secrets, prompt, timeout)
        except Exception as exc:
            last_exc = exc
            if attempt < retry:
                time.sleep(min(2 ** attempt, 8))
    assert last_exc is not None
    raise last_exc
