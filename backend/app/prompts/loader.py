from functools import lru_cache
from pathlib import Path

from app.config import get_settings


class PromptNotFoundError(FileNotFoundError):
    pass


class PromptRenderError(ValueError):
    pass


class PromptLoader:
    def __init__(self, prompts_dir: Path | None = None) -> None:
        settings = get_settings()
        self.prompts_dir = prompts_dir or settings.prompts_path
        self._cache: dict[str, str] = {}

    def _resolve_path(self, name: str) -> Path:
        # Allow subpaths like "civilization/goal_planner"
        rel = Path(name)
        if rel.suffix != ".md":
            rel = rel.with_suffix(".md")
        path = (self.prompts_dir / rel).resolve()
        base = self.prompts_dir.resolve()
        if not str(path).startswith(str(base)):
            raise PromptNotFoundError(f"Prompt path escapes prompts_dir: {name}")
        if not path.exists():
            raise PromptNotFoundError(f"Prompt not found: {path}")
        return path

    def load_raw(self, name: str) -> str:
        if name not in self._cache:
            path = self._resolve_path(name)
            self._cache[name] = path.read_text(encoding="utf-8")
        return self._cache[name]

    def render(self, name: str, **variables: object) -> str:
        """Replace only explicit {var} placeholders; leave JSON braces intact."""
        template = self.load_raw(name)
        result = template
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            if placeholder not in result:
                raise PromptRenderError(
                    f"Placeholder {placeholder} not found in prompt '{name}'"
                )
            result = result.replace(placeholder, str(value))
        return result

    def clear_cache(self) -> None:
        self._cache.clear()


@lru_cache
def get_prompt_loader() -> PromptLoader:
    return PromptLoader()
