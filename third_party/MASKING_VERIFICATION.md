# DDL masking verification – 5 cases

This document confirms that the five structural imputation cases match the intended DDL masking and are implemented correctly.

---

## 1. Case1Q1_T – **Schema: table name** (hide one table)

| Intended | Implementation | Status |
|----------|----------------|--------|
| Hide one table (table name not visible) | `mask_table(ddl, rng)`: finds all `CREATE TABLE` blocks, randomly removes **exactly one** block (full table including `) ENGINE=...;\n`). If schema has only 1 table, no mask. | OK |

- **Single/multi table:** N/A (one whole table removed).
- **Stored output:** `masked_ddl` has `(n_tables - 1)` tables; translation should describe only the remaining tables.

---

## 2. Case1Q2_T – **Schema: attributes** (hide attribute definitions)

| Intended | Implementation | Status |
|----------|----------------|--------|
| Hide attributes; keep structure (PK/FK/REFERENCES) | `mask_attributes(ddl)`: per table block, keeps only: `CREATE TABLE` line, lines containing `PRIMARY KEY`, `FOREIGN KEY`, or `REFERENCES`, and closing `)` / `) ENGINE=...`. Drops all plain column definitions. | OK |

- **Effect:** Model sees only table names and key/constraint structure, not column names or types.
- **Stored output:** `masked_ddl` has no `col type` lines; only PK/FK/REFERENCES and table headers.

---

## 3. Case1Q3_T – **Domain integrity: types, NULL/NOT NULL**

| Intended | Implementation | Status |
|----------|----------------|--------|
| Hide domain integrity: data types, NULL/NOT NULL (and DEFAULT, AUTO_INCREMENT) | `mask_domain_integrity(ddl)`: strips **data types** (INT, BIGINT, TINYINT, SMALLINT, VARCHAR(n), CHAR(n), TEXT, DATE, DATETIME, TIMESTAMP, DECIMAL(n,m), FLOAT, DOUBLE, ENUM/SET, etc.), **NULL/NOT NULL**, **DEFAULT ...**, **AUTO_INCREMENT**. Plain columns become `colname` only. Lines with `KEY ` or `CONSTRAINT ` are left unchanged. | OK |

- **Single/multi column:** N/A for domain (applies to every column).
- **Stored output:** Column lines have no types or nullability; KEY/CONSTRAINT lines unchanged.

---

## 4. Case1Q4_T – **Entity integrity: PRIMARY KEY, UNIQUE (single/multi column)**

| Intended | Implementation | Status |
|----------|----------------|--------|
| Hide entity integrity: PRIMARY KEY and UNIQUE (single and multi-column) | `mask_entity_integrity(ddl)`: removes (1) table-level `CONSTRAINT ... PRIMARY KEY (...)`; (2) standalone `PRIMARY KEY (col1, col2)`; (3) `UNIQUE KEY name (col)` / `UNIQUE (col)` / multi-column `UNIQUE (col1, col2)`; (4) `CONSTRAINT ... UNIQUE ...`; (5) inline `PRIMARY KEY` and `UNIQUE` on column lines. Cleans trailing comma before `)`. | OK |

- **Single/multi column:** Regex `PRIMARY\s+KEY\s*\([^)]+\)` and `UNIQUE\s+(?:KEY\s+)?(?:\([^)]+\)|\S+)` cover both (e.g. `(a)`, `(a,b)`).
- **Stored output:** No PRIMARY KEY or UNIQUE in `masked_ddl`; columns and non-unique KEYs remain.

---

## 5. Case1Q5_T – **Referential integrity: FOREIGN KEY (single/multi column)**

| Intended | Implementation | Status |
|----------|----------------|--------|
| Hide referential integrity: FOREIGN KEY and REFERENCES (single and multi-column) | `mask_referential_integrity(ddl)`: (1) removes entire line if it is `(CONSTRAINT name )? FOREIGN KEY (cols) REFERENCES ...` (any column list); (2) strips inline `REFERENCES table(col)` or `REFERENCES table(col1, col2)` from column lines. Cleans trailing comma before `)`. | OK |

- **Single/multi column:** `FOREIGN KEY (...)` uses `[^)]+` for column list; inline `REFERENCES` uses `\(\s*[^)]+\s*\)` for column list (fixed to support multi-column).
- **Stored output:** No FOREIGN KEY or REFERENCES in `masked_ddl`; columns and PK/UNIQUE/KEY remain.

---

## Summary

| Case   | Output dir    | Mask target                    | Masked correctly |
|--------|---------------|---------------------------------|------------------|
| Case1Q1_T | Case1Q1_T_*   | Table name (one table removed) | Yes              |
| Case1Q2_T | Case1Q2_T_*   | Attributes (only PK/FK/refs)    | Yes              |
| Case1Q3_T | Case1Q3_T_*   | Domain (types, NULL/NOT NULL)   | Yes              |
| Case1Q4_T | Case1Q4_T_*   | Entity (PRIMARY KEY, UNIQUE)    | Yes (single + multi) |
| Case1Q5_T | Case1Q5_T_*   | Referential (FOREIGN KEY, REFs) | Yes (single + multi) |

All five cases are aligned with the intended DDL masking; multi-column PRIMARY KEY, UNIQUE, and FOREIGN KEY / REFERENCES are handled. The only code change made was extending the inline `REFERENCES` removal in Case 5 to support multi-column references via `[^)]+` inside the parentheses.
