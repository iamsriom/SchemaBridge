"""Hash-verified prompt assets for the E1 (schema2text) and E2 (round-trip) reproductions.

The describer prompts are byte-exact copies of the texts used in the archived runs.  Every
load re-verifies the SHA-256 of the file bytes, so silent prompt drift raises immediately.

No network, no model calls, no files written.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "prompts"

# SHA-256 of the raw file bytes (no trailing newline in the describer files).
PROMPT_FILES: dict[str, str] = {
    "basic": "describer_basic.txt",
    "detailed": "describer_detailed.txt",
    "constructor": "constructor.txt",
}
EXPECTED_SHA256: dict[str, str] = {
    "basic": "e1422bc806119c375d89e44759feee44f13eb2717335154ad3c9ca933b6e6c20",
    "detailed": "f09fc8cae8d8ec73deb79f8bc7c2e71842d5fd35e92d833a02954b539755622d",
    "constructor": "392a396f7073bc015d206460055f7e3b8a3c94a21ed09c059bc47c13d3884ad4",
}
DESCRIBER_VARIANTS = ("basic", "detailed")


class PromptHashError(RuntimeError):
    """Raised when a prompt file does not match its pinned SHA-256."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prompt_path(name: str, prompt_dir: Path | None = None) -> Path:
    if name not in PROMPT_FILES:
        raise KeyError(f"unknown prompt {name!r}; expected one of {sorted(PROMPT_FILES)}")
    return (prompt_dir or PROMPT_DIR) / PROMPT_FILES[name]


def prompt_sha256(name: str, prompt_dir: Path | None = None) -> str:
    return sha256_bytes(prompt_path(name, prompt_dir).read_bytes())


def verify_prompt(name: str, prompt_dir: Path | None = None) -> str:
    """Return the actual SHA-256, raising PromptHashError on mismatch."""
    actual = prompt_sha256(name, prompt_dir)
    expected = EXPECTED_SHA256[name]
    if actual != expected:
        raise PromptHashError(
            f"prompt {name!r} ({PROMPT_FILES[name]}) hash mismatch: expected {expected}, got {actual}"
        )
    return actual


def verify_all_prompts(prompt_dir: Path | None = None) -> dict[str, str]:
    return {name: verify_prompt(name, prompt_dir) for name in PROMPT_FILES}


def load_prompt(name: str, prompt_dir: Path | None = None, *, verify: bool = True) -> str:
    """Load a prompt exactly as stored on disk (UTF-8, no stripping)."""
    if verify:
        verify_prompt(name, prompt_dir)
    return prompt_path(name, prompt_dir).read_text(encoding="utf-8")


def load_describer_system(variant: str, prompt_dir: Path | None = None) -> str:
    if variant not in DESCRIBER_VARIANTS:
        raise ValueError(f"unknown describer variant {variant!r}; expected {DESCRIBER_VARIANTS}")
    return load_prompt(variant, prompt_dir)


def load_constructor_system(prompt_dir: Path | None = None) -> str:
    return load_prompt("constructor", prompt_dir)


def count_tables(ddl: str) -> int:
    return len(re.findall(r"CREATE\s+TABLE", ddl, re.IGNORECASE))


def build_basic_user_message(database: str, ddl: str) -> str:
    """Basic (E1 'schema2text1') user message."""
    return f"Database name: {database}\n\nDDL:\n{ddl}"


def build_detailed_user_message(database: str, ddl: str) -> str:
    """Detailed (E1 'schema2text2') user message: table count plus explicit task lines."""
    return "\n".join(
        [
            f"Database name: {database}",
            f"Number of tables in schema: {count_tables(ddl)}",
            "",
            "DDL:",
            ddl,
            "",
            "Task: Write ONE continuous paragraph in plain English describing this entire schema.",
            "Do not output any SQL, DDL, bullet points, or section headers.",
        ]
    )


def build_describer_user_message(variant: str, database: str, ddl: str) -> str:
    if variant == "basic":
        return build_basic_user_message(database, ddl)
    if variant == "detailed":
        return build_detailed_user_message(database, ddl)
    raise ValueError(f"unknown describer variant {variant!r}; expected {DESCRIBER_VARIANTS}")


def build_constructor_user_message(nl_text: str, database: str) -> str:
    """E2 constructor user message (NL description -> JSON{ddl, metadata})."""
    return "\n".join(
        [
            f"Database name: {database}",
            "",
            "Natural language description:",
            nl_text,
        ]
    )


__all__ = [
    "DESCRIBER_VARIANTS",
    "EXPECTED_SHA256",
    "PROMPT_DIR",
    "PROMPT_FILES",
    "PromptHashError",
    "build_basic_user_message",
    "build_constructor_user_message",
    "build_describer_user_message",
    "build_detailed_user_message",
    "count_tables",
    "load_constructor_system",
    "load_describer_system",
    "load_prompt",
    "prompt_sha256",
    "verify_all_prompts",
    "verify_prompt",
]
