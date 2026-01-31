"""Minimal compatibility replacement for `pydantic_settings.BaseSettings`.

This provides just enough behavior for the repository's simple uses:
- load values from an optional `Config.env_file` (default ".env") into
  the environment
- respect `Config.env_prefix` when reading env vars
- cast basic types (int, float, bool, str)

This avoids requiring the external `pydantic-settings` package during tests.
"""
import os
import typing
from pathlib import Path


class BaseSettings:
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_prefix = ""
        extra = "ignore"

    def __init__(self):
        cfg = getattr(self, "Config", None)
        env_file = getattr(cfg, "env_file", ".env") if cfg is not None else ".env"
        env_prefix = getattr(cfg, "env_prefix", "") if cfg is not None else ""
        case_sensitive = getattr(cfg, "case_sensitive", True) if cfg is not None else True

        # load .env file into environment (do not override existing env vars)
        p = Path(env_file)
        if p.exists():
            for line in p.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    os.environ.setdefault(k, v)

        # populate fields from environment or class defaults
        annotations = getattr(self.__class__, "__annotations__", {})
        for field, _typ in annotations.items():
            env_name = f"{env_prefix}{field}"
            lookups = [env_name]
            if not case_sensitive:
                lookups.append(env_name.upper())

            raw = None
            for key in lookups:
                if key in os.environ:
                    raw = os.environ[key]
                    break

            if raw is None and hasattr(self.__class__, field):
                value = getattr(self.__class__, field)
            elif raw is None:
                value = None
            else:
                value = self._cast(raw, _typ)

            setattr(self, field, value)

    def _cast(self, raw: str, typ: typing.Any):
        try:
            origin = getattr(typ, "__origin__", None)
            if origin is typing.Union:
                # Optional[T] or Union[T, None]
                args = getattr(typ, "__args__", [])
                typ = args[0] if args else str

            if typ is int:
                return int(raw)
            if typ is float:
                return float(raw)
            if typ is bool:
                return raw.lower() in ("1", "true", "yes", "on")
            return raw
        except Exception:
            return raw


__all__ = ["BaseSettings"]
