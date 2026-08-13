"""Tool registry with role-based permissions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.agents.roles import AgentRole, permissions_for_role
from app.config import get_settings

ToolHandler = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    required_permission: str
    requires_global_flag: str | None = None  # e.g. enable_web_tools


ALL_TOOL_NAMES = frozenset(
    {
        "search_web",
        "read_file",
        "write_file",
        "edit_file",
        "execute_python",
        "create_project",
        "create_business",
        "buy_asset",
        "sell_asset",
        "take_loan",
        "repay_loan",
        "hire_worker",
        "fire_worker",
        "start_construction",
        "complete_construction",
    }
)


TOOL_DEFINITIONS: dict[str, ToolDefinition] = {
    "search_web": ToolDefinition(
        "search_web",
        "Search the web for market or technical information",
        "search_web",
        "enable_web_tools",
    ),
    "read_file": ToolDefinition(
        "read_file",
        "Read a file from the agent workspace",
        "read_file",
        "enable_file_tools",
    ),
    "write_file": ToolDefinition(
        "write_file",
        "Write a new file in the agent workspace",
        "write_file",
        "enable_file_tools",
    ),
    "edit_file": ToolDefinition(
        "edit_file",
        "Edit an existing file in the agent workspace",
        "edit_file",
        "enable_file_tools",
    ),
    "execute_python": ToolDefinition(
        "execute_python",
        "Run Python in a sandboxed interpreter (software roles only)",
        "execute_python",
        "enable_execute_python",
    ),
    "create_project": ToolDefinition("create_project", "Create a generic project record", "create_project"),
    "create_business": ToolDefinition("create_business", "Register a new business", "create_business"),
    "buy_asset": ToolDefinition("buy_asset", "Purchase an asset", "buy_asset"),
    "sell_asset": ToolDefinition("sell_asset", "Sell an owned asset", "sell_asset"),
    "take_loan": ToolDefinition("take_loan", "Borrow money from the village bank", "take_loan"),
    "repay_loan": ToolDefinition("repay_loan", "Repay an outstanding loan", "repay_loan"),
    "hire_worker": ToolDefinition("hire_worker", "Hire a human or AI worker", "hire_worker"),
    "fire_worker": ToolDefinition("fire_worker", "Release a worker", "fire_worker"),
    "start_construction": ToolDefinition("start_construction", "Begin a construction project", "start_construction"),
    "complete_construction": ToolDefinition(
        "complete_construction", "Mark a construction project complete", "complete_construction"
    ),
}


class ToolRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, ToolHandler] = {}

    def register(self, name: str, handler: ToolHandler) -> None:
        if name not in ALL_TOOL_NAMES:
            raise ValueError(f"Unknown tool: {name}")
        self._handlers[name] = handler

    def get_handler(self, name: str) -> ToolHandler | None:
        return self._handlers.get(name)

    def list_tools_for_role(self, role: AgentRole | str) -> list[dict[str, str]]:
        perms = permissions_for_role(role)
        settings = get_settings()
        out: list[dict[str, str]] = []
        for name, defn in TOOL_DEFINITIONS.items():
            if defn.required_permission not in perms:
                continue
            if defn.requires_global_flag and not getattr(settings, defn.requires_global_flag, False):
                continue
            out.append({"name": name, "description": defn.description})
        return out

    def can_use(self, role: AgentRole | str, tool_name: str) -> tuple[bool, str | None]:
        if tool_name not in ALL_TOOL_NAMES:
            return False, f"Unknown tool: {tool_name}"
        defn = TOOL_DEFINITIONS[tool_name]
        perms = permissions_for_role(role)
        if defn.required_permission not in perms:
            return False, f"Role '{role}' lacks permission for '{tool_name}'"
        settings = get_settings()
        if defn.requires_global_flag and not getattr(settings, defn.requires_global_flag, False):
            return False, f"Tool '{tool_name}' is disabled in server settings"
        if tool_name not in self._handlers:
            return False, f"Tool '{tool_name}' is not registered"
        return True, None


_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    global _registry
    if _registry is None:
        from app.tools.implementations import register_all_tools

        _registry = ToolRegistry()
        register_all_tools(_registry)
    return _registry
