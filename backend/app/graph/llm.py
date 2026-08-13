import ast
import json
import logging
import re
from typing import Any

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import get_settings
from app.prompts.loader import get_prompt_loader

logger = logging.getLogger(__name__)

JSON_SYSTEM = (
    "You must respond with a single valid JSON object only. "
    "Use double quotes for all keys and strings. No markdown fences. No commentary."
)


def get_chat_model(temperature: float = 0.7, *, json_mode: bool = False) -> ChatOllama:
    settings = get_settings()
    kwargs: dict[str, Any] = {
        "base_url": settings.ollama_base_url,
        "model": settings.ollama_model,
        "temperature": temperature,
    }
    if json_mode:
        kwargs["format"] = "json"
    return ChatOllama(**kwargs)


def _strip_json_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text)
    return text.strip()


def _find_balanced_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escape = False
    quote = ""
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                in_string = False
            continue
        if ch in ('"', "'"):
            in_string = True
            quote = ch
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _eval_simple_math(expr: str) -> str:
    """Best-effort numeric eval for LLM math like '3450.0 + (-1000.0)'."""
    expr = expr.strip()
    if "=" in expr:
        expr = expr.split("=")[-1].strip()
    if not re.fullmatch(r"[\d\.\+\-\*\/\(\)\s]+", expr):
        return expr
    try:
        value = eval(expr, {"__builtins__": {}}, {})  # noqa: S307 — sandboxed literals only
        if isinstance(value, (int, float)):
            return str(float(value))
    except Exception:
        pass
    return expr


def _fix_math_expressions(text: str) -> str:
    """Small models emit invalid JSON like: 3450.0 + (-1000.0) = 2450.0"""
    # Expression with equals sign → keep RHS number
    text = re.sub(
        r"(:\s*)(-?\d+(?:\.\d+)?(?:\s*[\+\-\*\/]\s*\(?-?\d+(?:\.\d+)?\)?\s*)+\s*=\s*)(-?\d+(?:\.\d+)?)",
        r"\1\3",
        text,
    )
    # Bare arithmetic without equals
    def _repl(m: re.Match[str]) -> str:
        return f": {_eval_simple_math(m.group(1))}"

    text = re.sub(
        r":\s*(-?\d+(?:\.\d+)?(?:\s*[\+\-\*\/]\s*\(?-?\d+(?:\.\d+)?\)?)+)(?=\s*[,}\]])",
        _repl,
        text,
    )
    return text


def _repair_json_text(text: str) -> str:
    text = _strip_json_fences(text)
    # Drop leading junk before first {
    brace = text.find("{")
    if brace > 0:
        text = text[brace:]
    text = _fix_math_expressions(text)
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    # Single-quoted keys/strings → double quotes (common small-model mistake)
    text = re.sub(r"'([^'\\]*?)'", r'"\1"', text)
    return text


def _parse_with_literal_eval(text: str) -> dict[str, Any] | None:
    blob = _find_balanced_object(text) or text
    try:
        value = ast.literal_eval(blob)
        if isinstance(value, dict):
            return value
    except (SyntaxError, ValueError):
        pass
    return None


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = _repair_json_text(text)
    parsers: list[tuple[str, Any]] = [
        ("json.loads", lambda t: json.loads(t)),
        ("balanced", lambda t: json.loads(_find_balanced_object(t) or t)),
        ("literal_eval", lambda t: _parse_with_literal_eval(t)),
    ]
    errors: list[str] = []
    for name, fn in parsers:
        try:
            result = fn(cleaned)
            if isinstance(result, dict):
                return result
        except Exception as exc:
            errors.append(f"{name}: {exc}")
    logger.debug("JSON parse failures: %s | raw=%s", errors, cleaned[:500])
    raise json.JSONDecodeError(
        f"Could not parse LLM JSON ({'; '.join(errors)})", cleaned, 0
    )


def _mock_json(prompt: str) -> dict[str, Any]:
    """Deterministic responses for tests when MOCK_LLM=true."""
    p = prompt.lower()
    if "event engine" in p or "generate 1-5 events" in p:
        return {
            "events": [
                {
                    "event_id": "evt_mock_1",
                    "title": "Power outage at the market",
                    "category": "Weather",
                    "description": "Electricity failed for two hours.",
                    "affected_agents": [],
                    "importance": 0.55,
                    "expected_consequences": ["Shopkeepers upset"],
                }
            ]
        }
    if "conversation engine" in p:
        return {
            "conversation": [
                {"speaker": "Rohit Patil", "message": "The tractor again!", "emotion": "Frustrated"},
                {"speaker": "Mahesh Patil", "message": "Let it go, Rohit.", "emotion": "Calm"},
            ],
            "important_moments": ["Heated exchange about finances"],
        }
    if "memory manager" in p:
        return {
            "new_memories": [
                {
                    "agent_id": "patil_001",
                    "memory": "Argued about tractor purchase at tea stall",
                    "emotion": "Frustrated",
                    "importance": 0.6,
                    "participants": ["Rohit Patil", "Mahesh Patil"],
                    "timestamp": "Day 1 Morning",
                }
            ]
        }
    if "relationship manager" in p:
        return {
            "updates": [
                {
                    "agent_a": "patil_001",
                    "agent_b": "patil_002",
                    "friendship_change": -5,
                    "trust_change": -3,
                    "respect_change": 0,
                    "rivalry_change": 8,
                    "reason": "Financial argument",
                }
            ]
        }
    if "emotion engine" in p:
        return {"emotion": "Frustrated", "intensity": 0.6, "reason": "Family argument"}
    if "gossip engine" in p:
        return {
            "rumors": [
                {
                    "rumor_id": "rumor_mock_1",
                    "content": "Someone says the tractor was bought on credit",
                    "source_agent_id": "",
                    "spread_to_agents": [],
                    "truth_level": 0.5,
                    "distortion_level": 0.2,
                    "importance": 0.45,
                }
            ],
            "updated_rumors": [],
        }
    if "story feed engine" in p or "feed_entries" in p:
        return {
            "feed_entries": [
                {
                    "story_id": "story_mock_1",
                    "title": "Tea Stall Argument Over New Tractor",
                    "summary": "A discussion about a tractor turned heated.",
                    "full_story": "At the tea stall, villagers debated a recent purchase.",
                    "timestamp": "Day 1 Morning",
                    "date": "Day 1",
                    "time": "Morning",
                    "location": "Tea Stall",
                    "category": "Gossip",
                    "importance": 0.72,
                    "participants": ["Rohit Patil", "Mahesh Patil"],
                    "families": ["Patil"],
                    "tags": ["Gossip", "Tractor"],
                    "keywords": ["tractor", "tea stall"],
                    "future_hooks": ["Rivalry may continue"],
                }
            ]
        }
    return {}


def _invoke_ollama_json(prompt: str, temperature: float) -> dict[str, Any]:
    last_error: Exception | None = None
    last_raw: str = ""
    for attempt in range(3):
        # Ollama format=json on first attempt — critical for llama3.2:1b
        model = get_chat_model(temperature=temperature, json_mode=True)
        messages = [
            SystemMessage(content=JSON_SYSTEM),
            HumanMessage(
                content=prompt
                if attempt == 0
                else prompt
                + "\n\nREMINDER: Reply with ONE JSON object only. Double-quoted keys. "
                'Start with { and end with }. Example: {"feed_entries":[]}'
            ),
        ]
        try:
            response = model.invoke(messages)
            content = response.content if isinstance(response.content, str) else str(response.content)
            last_raw = content[:800]
            return _extract_json_object(content)
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                logger.debug(
                    "LLM JSON parse attempt %s failed: %s | snippet=%s",
                    attempt + 1,
                    exc,
                    last_raw[:200],
                )
            else:
                logger.warning(
                    "LLM JSON parse failed after %s attempts: %s | snippet=%s",
                    attempt + 1,
                    exc,
                    last_raw[:200],
                )
    raise RuntimeError(f"Failed to get valid JSON from Ollama: {last_error}") from last_error


def invoke_json(prompt: str, temperature: float = 0.4) -> dict[str, Any]:
    if get_settings().mock_llm:
        return _mock_json(prompt)
    return _invoke_ollama_json(prompt, temperature)


def world_context(max_chars: int = 4000) -> str:
    loader = get_prompt_loader()
    parts: list[str] = []
    for name in ("world_prompt", "village_lore"):
        try:
            parts.append(loader.load_raw(name))
        except FileNotFoundError:
            continue
    if not parts:
        return ""
    text = "\n\n".join(parts)
    return text[:max_chars] if len(text) > max_chars else text
