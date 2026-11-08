# Datasets

Place raw or derived schema corpora outside git when large; track **manifests** here that point at record IDs and splits.

## Manifests

`manifests/` holds JSONL index files, one record per line, for example:

```json
{"id": "0001", "split": "test", "source": "annotation_ddl", "path": "..."}
```

Recommended manifests:

| File | Used by |
|------|---------|
| `default.jsonl` | E0 |
| `text2schema.jsonl` | E1 |
| `schema2text.jsonl` | E2 |
| `masking.jsonl` | E3 |

## Notes

- Do not commit proprietary DDL dumps or API keys.
- Prefer relative paths from the repo root in manifest entries.
