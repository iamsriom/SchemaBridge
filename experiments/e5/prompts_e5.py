"""Exact E1/E2 prompts for E5 (no prompt drift)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = ROOT / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / name).read_text(encoding="utf-8").strip()


BASIC_SYSTEM = load_prompt("describer_basic.txt")
DETAILED_SYSTEM = load_prompt("describer_detailed.txt")
CONSTRUCTOR_SYSTEM = load_prompt("constructor.txt")


def n_tables(ddl: str) -> int:
    return len(re.findall(r"CREATE\s+TABLE", ddl, re.IGNORECASE))


def describer_user_content(database: str, ddl: str, prompt_variant: str) -> str:
    """User message matching archived Exp4 basic builder; detailed asks for five sections."""
    n = n_tables(ddl)
    if prompt_variant == "basic":
        return "\n".join(
            [
                f"Database name: {database}",
                f"Number of tables in schema: {n}",
                "",
                "DDL:",
                ddl,
                "",
                "Task: Write ONE continuous paragraph in plain English describing this entire schema.",
                "Do not output any SQL, DDL, bullet points, or section headers.",
            ]
        )
    if prompt_variant == "detailed":
        return "\n".join(
            [
                f"Database name: {database}",
                f"Number of tables in schema: {n}",
                "",
                "DDL:",
                ddl,
                "",
                "Task: Translate this schema into the five-section natural-language description "
                "required by your instructions (TABLES, ATTRIBUTES, DOMAIN INTEGRITY, "
                "ENTITY INTEGRITY, REFERENTIAL INTEGRITY). Do not output SQL or DDL.",
            ]
        )
    raise ValueError(prompt_variant)


def constructor_user_content(nl_text: str, database: str, text_number: int | None = None) -> str:
    parts = []
    if text_number is not None:
        parts.append(f"Text number: {text_number} (schema serial index in dataset)")
    parts.extend(
        [
            f"Database name: {database}",
            "",
            "Natural language description:",
            nl_text,
            "",
            "Reminder: extract all entities, all named attributes, junction tables for M:N links, "
            "and FOREIGN KEYs for every cross-entity ID reference. Do not merge distinct entities.",
        ]
    )
    return "\n".join(parts)


def system_for_describer(prompt_variant: str) -> str:
    if prompt_variant == "basic":
        return BASIC_SYSTEM
    if prompt_variant == "detailed":
        return DETAILED_SYSTEM
    raise ValueError(prompt_variant)
