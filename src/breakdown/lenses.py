"""The research goal's conceptual framework as a lens on each variable (config/lenses.yaml): longest prefix wins."""

from __future__ import annotations

from pathlib import Path

import yaml

from .model import BuildError


class Lenses:
    def __init__(self, path: Path):
        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.lenses: dict[str, dict] = cfg["lenses"]
        self.rules: dict[str, dict[str, str]] = {k: v for k, v in cfg.items() if k not in ("lenses", "default")}
        self.default: dict[str, str] = cfg.get("default", {})
        for family, rules in [*self.rules.items(), ("default", self.default)]:
            for prefix, lens in rules.items():
                if lens not in self.lenses:
                    raise BuildError(f"config/lenses.yaml: {family} rule {prefix!r} names an unknown lens {lens!r}")

    def of(self, family: str, code: str = "") -> str:
        if family in self.default:
            return self.default[family]
        rules = self.rules.get(family)
        if rules is None:
            raise BuildError(f"config/lenses.yaml: no rules or default for {family!r}")
        best = max((p for p in rules if code.startswith(p)), key=len, default=None)
        if best is None:
            raise BuildError(f'config/lenses.yaml: no {family} rule covers {code!r} (add a "" rule as the fallback)')
        return rules[best]
