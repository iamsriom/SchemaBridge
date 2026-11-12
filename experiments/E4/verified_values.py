"""Authoritative E4 manuscript values (ICDE 2027) — joint Domain, pooled datasets.

Frozen after the E4 final verification audit. Do not substitute older Exp5
domain_facts cells or SchemaBench-only Domain extracts.
"""
from __future__ import annotations

# Split: Direct GPT-4o-mini micro recall by inferability (observed-case rows).
# Domain uses joint type-family + nullability per column (unique columns).
E4_SPLIT = {
    "MT Tables": {
        "inferable": {"recall": 0.350, "gold_n": 2555},
        "non_inferable": {"recall": 0.197, "gold_n": 4272},
    },
    "MA Attributes": {
        "inferable": {"recall": 0.611, "gold_n": 9254},
        "non_inferable": {"recall": 0.187, "gold_n": 42594},
    },
    "MD Domain": {
        "inferable": {"recall": 0.196, "gold_n": 8578},
        "non_inferable": {"recall": 0.451, "gold_n": 36669},
    },
    "ME Entity": {
        "inferable": {"recall": 0.871, "gold_n": 2161},
        "non_inferable": {"recall": 0.447, "gold_n": 2608},
    },
    "MR Referential": {
        "inferable": {"recall": 0.687, "gold_n": 4214},
        "non_inferable": {"recall": 0.288, "gold_n": 1246},
    },
}

# Recovery: unique inferable elements; RT = per-element mean over available describers.
E4_RECOVERY = {
    "MT Tables": {"gold_n": 2555, "direct": 0.350, "rt": 0.120, "retention": 0.344},
    "MA Attributes": {"gold_n": 9254, "direct": 0.611, "rt": 0.487, "retention": 0.797},
    "MD Domain": {"gold_n": 8578, "direct": 0.196, "rt": 0.049, "retention": 0.251},
    "ME Entity": {"gold_n": 2087, "direct": 0.877, "rt": 0.624, "retention": 0.712},
    "MR Referential": {"gold_n": 4197, "direct": 0.688, "rt": 0.444, "retention": 0.645},
}

DOMAIN_DEFINITION = (
    "Joint matching of data-type family and nullability (same structural Domain "
    "definition used elsewhere in SchemaBridge). Legacy Exp5 domain_facts scoring "
    "is historical and is not the paper Domain metric."
)

RT_AGGREGATION = (
    "For each eligible gold element, average the match indicator over available "
    "describers; micro-average those element-level means; Retention = RT/Direct "
    "at full precision before rounding to three decimals."
)

POPULATION_NOTE = (
    "Split Entity/Referential Gold N use Direct evaluation-row micro counts "
    "(including rare duplicate Direct rows). Recovery Gold N uses unique eligible "
    "elements in the paired Direct/RT population (Entity 2087 vs 2161; "
    "Referential 4197 vs 4214). Tables/Attributes/Domain Gold N match across tables."
)
