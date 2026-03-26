from __future__ import annotations

from pathlib import Path

import yaml


def get_provider_info() -> dict:
    provider_yaml = Path(__file__).with_name("provider.yaml")
    return yaml.safe_load(provider_yaml.read_text(encoding="utf-8"))
