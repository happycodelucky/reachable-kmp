"""
mkdocs-macros entry point for the Reachable docs site.

Exposes a `version` variable that markdown can reference as `{{ version }}`
for install snippets, version-pinning notes, etc.

`version` resolution order:
  1. REACHABLE_VERSION env var — the Release workflow passes the version it
     just published when it deploys the site (docs.yml).
  2. `version=` in gradle.properties: the last version released from main,
     bumped by each release PR (scripts/changeset.py). No network, no `gh`.
  3. `main` — nothing released yet (0.0.0). The rendered docs then say
     `implementation("...:main")`, a clear "you're viewing a development
     build" signal rather than a misleading made-up version.

No one edits markdown when cutting a release: the version flows from the
release PR's bump.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

GRADLE_PROPERTIES = Path(__file__).resolve().parent / "gradle.properties"


def _committed_version() -> str | None:
    """`version=` from gradle.properties, or None if absent or unreleased."""
    try:
        text = GRADLE_PROPERTIES.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"^version[ \t]*[=:][ \t]*(\S+)", text, re.MULTILINE)
    if not match or match.group(1) == "0.0.0":
        return None
    return match.group(1)


def _resolve_version() -> str:
    """Compute the version string the docs should render."""
    env_version = os.environ.get("REACHABLE_VERSION", "").strip()
    if env_version:
        return env_version.lstrip("v")

    return _committed_version() or "main"


def define_env(env):  # noqa: ANN001 (mkdocs-macros API)
    """mkdocs-macros entry point — register variables and filters."""
    env.variables["version"] = _resolve_version()
