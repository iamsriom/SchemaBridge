"""Vendored shim for ``RSchemaCode/evaluate_rschema_predictions.py`` (SchemaBridge).

``evaluate_exp4_text2schema.py`` only needs three names from the original module:
``gold_answer_to_metadata_and_ddl``, ``load_jsonl`` and ``normalize_rschema_name``.
They are re-exported from the self-contained SchemaBridge ``src`` package so that the
vendored evaluator runs without any ``/data/...`` checkout when ``SCHEMABRIDGE_ROOT``
is set (the repo root must then be on ``sys.path``; the evaluator does that).
"""
from src.evaluator import gold_answer_to_metadata_and_ddl, load_jsonl  # noqa: F401
from src.normalization import normalize_rschema_name  # noqa: F401
