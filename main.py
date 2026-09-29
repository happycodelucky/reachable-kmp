"""
mkdocs-macros entry point for the Reachable docs site.

Exposes a `version` variable that markdown can reference as `{{ version }}`
for install snippets, version-pinning notes, etc., and an `api_reference()`
macro that renders the committed public-API dumps (docs/reference.md).

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


# A klib dump line's trailing ABI signature: ` // com.x/Type.member|member(){}[0]`.
_SIGNATURE = re.compile(r"\s+// [^|\s]+\|.*$")


def _api_surface(dump: Path) -> str:
    """A committed klib ABI dump as plain declarations: the header and each
    line's trailing ABI signature dropped. Per-target comments stay."""
    lines = dump.read_text(encoding="utf-8").splitlines()
    while lines and (lines[0].startswith("//") or not lines[0].strip()):
        lines.pop(0)  # header: dump format, targets, library unique name
    body = "\n".join(_SIGNATURE.sub("", line) for line in lines)
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def api_reference() -> str:
    """Markdown for every published module's public API, read from the
    committed dumps (<module>/api/<module>.klib.api) — which `mise run check`
    keeps identical to the code. Modules are discovered, not named, so a new
    published module appears without touching this file."""
    root = GRADLE_PROPERTIES.parent
    dumps = sorted(root.glob("*/api/*.klib.api"))
    if not dumps:
        return "_No API dump yet — run `mise run api:dump` and commit the `api/` directories._"
    return "\n\n".join(
        f"## `{dump.parent.parent.name}`\n\n```text\n{_api_surface(dump)}\n```" for dump in dumps
    )


def define_env(env):  # noqa: ANN001 (mkdocs-macros API)
    """mkdocs-macros entry point — register variables and filters."""
    env.variables["version"] = _resolve_version()
    env.macro(api_reference)
