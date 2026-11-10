"""The 13 mandatory DDL regression cases for the corrected SchemaBench parser.

Every case is asserted against the robust parser (``legacy=False``, the default).  Where the
vendored/legacy parser behaves differently, a separate characterisation test pins that
behaviour so that the difference is documented rather than silent.
"""
import pytest

from src.schema_parser import (
    _parse_data_type,
    ensure_prediction_metadata,
    iter_ddl_table_bodies,
    metadata_from_ddl,
    parse_ddl,
    parse_ddl_fks,
    parse_ddl_primary_unique,
)


def cols(meta, table):
    return [c["COLUMN_NAME"] for c in meta["columns_by_table"][table]]


def col(meta, table, name):
    return next(c for c in meta["columns_by_table"][table] if c["COLUMN_NAME"] == name)


# 1 -------------------------------------------------------------------------
@pytest.mark.parametrize("legacy", [False, True])
def test_01_create_table_if_not_exists(legacy):
    ddl = "CREATE TABLE IF NOT EXISTS `users` (\n  `id` int NOT NULL,\n  `name` varchar(50)\n);"
    meta = metadata_from_ddl(ddl, legacy=legacy)
    assert meta["tables"] == ["users"]
    assert cols(meta, "users") == ["id", "name"]
    assert [t for t, _ in iter_ddl_table_bodies(ddl, legacy=legacy)] == ["users"]


def test_01_if_not_exists_fk_source_table_is_not_IF():
    ddl = (
        "CREATE TABLE IF NOT EXISTS child (\n  pid int,\n  FOREIGN KEY (pid) REFERENCES parent (id)\n);"
    )
    fks, _ = parse_ddl_fks(ddl)
    assert fks == [("child", ["pid"], "parent", ["id"])]
    # characterisation of the vendored bug (kept for reproducing old numbers)
    legacy_fks, _ = parse_ddl_fks(ddl, legacy=True)
    assert legacy_fks[0][0] == "IF"


# 2 -------------------------------------------------------------------------
@pytest.mark.parametrize("legacy", [False, True])
def test_02_create_table_without_engine(legacy):
    ddl = "CREATE TABLE t (\n  a int,\n  b text\n)"  # no ENGINE, no semicolon
    meta = metadata_from_ddl(ddl, legacy=legacy)
    assert meta["tables"] == ["t"] and cols(meta, "t") == ["a", "b"]


def test_02_with_engine_and_charset_same_result():
    plain = metadata_from_ddl("CREATE TABLE t (a int, b text)")
    engine = metadata_from_ddl("CREATE TABLE `t` (\n `a` int,\n `b` text\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;")
    assert cols(plain, "t") == cols(engine, "t")


# 3 -------------------------------------------------------------------------
@pytest.mark.parametrize("legacy", [False, True])
def test_03_inline_primary_key(legacy):
    ddl = "CREATE TABLE t (\n  id int PRIMARY KEY,\n  v text\n);"
    pks, uqs = parse_ddl_primary_unique(ddl, legacy=legacy)
    assert pks == [("t", ["id"])] and uqs == []
    assert col(metadata_from_ddl(ddl, legacy=legacy), "t", "id")["COLUMN_KEY"] == "PRI"


# 4 -------------------------------------------------------------------------
@pytest.mark.parametrize("legacy", [False, True])
def test_04_inline_unique(legacy):
    ddl = "CREATE TABLE t (\n  id int,\n  email varchar(80) UNIQUE NOT NULL\n);"
    pks, uqs = parse_ddl_primary_unique(ddl, legacy=legacy)
    assert pks == [] and uqs == [("t", ["email"])]
    assert col(metadata_from_ddl(ddl, legacy=legacy), "t", "email")["COLUMN_KEY"] == "UNI"


def test_04_table_level_unique_robust_vs_legacy():
    ddl = "CREATE TABLE t (\n  a int,\n  b int,\n  UNIQUE (a, b)\n);"
    assert parse_ddl_primary_unique(ddl)[1] == [("t", ["a", "b"])]
    assert parse_ddl_primary_unique(ddl, legacy=True)[1] == []  # vendored parser ignores it


# 5 -------------------------------------------------------------------------
@pytest.mark.parametrize("legacy", [False, True])
def test_05_composite_primary_key(legacy):
    ddl = "CREATE TABLE t (\n  a int,\n  b int,\n  PRIMARY KEY (`a`, `b`)\n);"
    pks, _ = parse_ddl_primary_unique(ddl, legacy=legacy)
    assert pks == [("t", ["a", "b"])]


# 6 -------------------------------------------------------------------------
@pytest.mark.parametrize("legacy", [False, True])
def test_06_composite_foreign_key(legacy):
    ddl = (
        "CREATE TABLE p (a int, b int, PRIMARY KEY (a, b));\n"
        "CREATE TABLE c (\n  x int,\n  y int,\n"
        "  CONSTRAINT fk1 FOREIGN KEY (x, y) REFERENCES p (a, b)\n);"
    )
    fks, n_comp = parse_ddl_fks(ddl, legacy=legacy)
    assert fks == [("c", ["x", "y"], "p", ["a", "b"])]
    assert n_comp == 1


# 7 -------------------------------------------------------------------------
def test_07_quoted_names_with_spaces():
    ddl = (
        'CREATE TABLE "Order Items" (\n'
        '  "Item Id" INTEGER PRIMARY KEY,\n'
        '  "Unit Price" decimal(10,2) NOT NULL,\n'
        '  "Order Id" int,\n'
        '  FOREIGN KEY ("Order Id") REFERENCES "Customer Orders" ("Order Id")\n'
        ");"
    )
    meta = metadata_from_ddl(ddl)
    assert meta["tables"] == ["Order Items"]
    assert cols(meta, "Order Items") == ["Item Id", "Unit Price", "Order Id"]
    assert parse_ddl_primary_unique(ddl)[0] == [("Order Items", ["Item Id"])]
    assert parse_ddl_fks(ddl)[0] == [("Order Items", ["Order Id"], "Customer Orders", ["Order Id"])]


# 8 -------------------------------------------------------------------------
def test_08_backtick_identifiers_are_unquoted():
    ddl = "CREATE TABLE `my_table` (\n  `my col` varchar(10),\n  `id` int,\n  PRIMARY KEY (`id`)\n);"
    meta = metadata_from_ddl(ddl)
    assert meta["tables"] == ["my_table"]
    assert cols(meta, "my_table") == ["my col", "id"]
    assert parse_ddl_primary_unique(ddl)[0] == [("my_table", ["id"])]


# 9 -------------------------------------------------------------------------
def test_09_foreign_key_direction_is_child_to_parent():
    ddl = (
        "CREATE TABLE parent (id int PRIMARY KEY);\n"
        "CREATE TABLE child (id int PRIMARY KEY, parent_id int,\n"
        "  FOREIGN KEY (parent_id) REFERENCES parent (id));"
    )
    fks, _ = parse_ddl_fks(ddl)
    assert fks == [("child", ["parent_id"], "parent", ["id"])]
    assert ("parent", ["id"], "child", ["parent_id"]) not in fks


def test_09_inline_references_direction():
    ddl = "CREATE TABLE parent (id int);\nCREATE TABLE child (pid int REFERENCES parent(id));"
    assert parse_ddl_fks(ddl)[0] == [("child", ["pid"], "parent", ["id"])]


# 10 ------------------------------------------------------------------------
def test_10_nullability_legacy_vendored():
    ddl = (
        "CREATE TABLE t (\n"
        "  a int NOT NULL,\n  b int NULL,\n  c int DEFAULT NULL,\n  d int,\n  e varchar(5) NOT NULL DEFAULT 'x'\n);"
    )
    meta = metadata_from_ddl(ddl, legacy=True)
    got = {c["COLUMN_NAME"]: c["IS_NULLABLE"] for c in meta["columns_by_table"]["t"]}
    # vendored: YES only with an explicit NULL and no NOT NULL; bare -> NO
    assert got == {"a": "NO", "b": "YES", "c": "YES", "d": "NO", "e": "NO"}


def test_10_nullability_mysql_dialect_default():
    ddl = (
        "CREATE TABLE t (\n"
        "  a int NOT NULL,\n  b int NULL,\n  c int DEFAULT NULL,\n  d int,\n"
        "  e varchar(5) NOT NULL DEFAULT 'x',\n  id int PRIMARY KEY\n);"
    )
    meta = metadata_from_ddl(ddl, legacy=False)
    got = {c["COLUMN_NAME"]: (c["IS_NULLABLE"], c["NULLABILITY_STATUS"]) for c in meta["columns_by_table"]["t"]}
    assert got["a"] == ("NO", "explicit_not_null")
    assert got["b"] == ("YES", "explicit_null")
    assert got["c"] == ("YES", "explicit_null")
    assert got["d"] == ("YES", "dialect_default")  # MySQL: bare column nullable
    assert got["e"] == ("NO", "explicit_not_null")
    assert got["id"] == ("NO", "primary_key")


# 11 ------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text,expected",
    [
        ("INTEGER NOT NULL", ("int", "int(11)")),
        ("int(10) unsigned", ("int", "int(11)")),
        ("BIGINT", ("bigint", "bigint")),
        ("VARCHAR(50)", ("varchar", "varchar(50)")),
        ("char(6)", ("char", "char(6)")),
        ("DECIMAL(10,2)", ("decimal", "decimal(10,2)")),
        ("DATETIME", ("datetime", "datetime")),
        ("BOOLEAN", ("boolean", "boolean")),
        ("BLOB", ("blob", "blob")),
        ("JSON", ("json", "json")),
        ("ENUM('a','b')", ("enum", "enum('a','b')")),
        ("VARBINARY(16)", ("varbinary", "varbinary(16)")),
        ("LONGTEXT", ("longtext", "longtext")),
    ],
)
def test_11_data_type_normalization(text, expected):
    assert _parse_data_type(text, legacy=False) == expected


def test_11_unknown_type_no_fabricated_varchar_robust():
    assert _parse_data_type("somethingweird", legacy=False) == ("", "")
    assert _parse_data_type("somethingweird", legacy=True) == ("varchar", "varchar(255)")


def test_11_integer_column_becomes_int_in_metadata():
    meta = metadata_from_ddl("CREATE TABLE t (\n  id INTEGER,\n  n VARCHAR(20)\n);")
    assert col(meta, "t", "id")["DATA_TYPE"] == "int"
    assert col(meta, "t", "n")["CHARACTER_MAXIMUM_LENGTH"] == 255


# 12 ------------------------------------------------------------------------
def test_12_escaped_identifiers():
    ddl = (
        "CREATE TABLE `we``ird` (\n"
        "  `a``b` int PRIMARY KEY,\n"
        '  "say ""hi""" text,\n'
        "  `x` int,\n"
        "  FOREIGN KEY (`x`) REFERENCES `we``ird` (`a``b`)\n);"
    )
    meta = metadata_from_ddl(ddl)
    assert meta["tables"] == ["we`ird"]
    assert cols(meta, "we`ird") == ["a`b", 'say "hi"', "x"]
    assert parse_ddl_fks(ddl)[0] == [("we`ird", ["x"], "we`ird", ["a`b"])]


def test_12_parentheses_inside_quoted_names_do_not_break_body():
    ddl = "CREATE TABLE `a(b` (\n  `c)d` int,\n  e int\n);\nCREATE TABLE z (q int);"
    meta = metadata_from_ddl(ddl)
    assert meta["tables"] == ["a(b", "z"]
    assert cols(meta, "a(b") == ["c)d", "e"]


# 13 ------------------------------------------------------------------------
def test_13_multiple_constraints_in_one_statement():
    ddl = (
        "CREATE TABLE child (\n"
        "  id int NOT NULL,\n"
        "  code varchar(10) UNIQUE,\n"
        "  a int,\n  b int,\n  pid int,\n"
        "  PRIMARY KEY (id),\n"
        "  UNIQUE KEY uq_ab (a, b),\n"
        "  FOREIGN KEY (pid) REFERENCES parent (id),\n"
        "  CONSTRAINT fk_ab FOREIGN KEY (a, b) REFERENCES other (x, y)\n"
        ") ENGINE=InnoDB;"
    )
    pks, uqs = parse_ddl_primary_unique(ddl)
    assert pks == [("child", ["id"])]
    assert sorted(uqs) == [("child", ["a", "b"]), ("child", ["code"])]
    fks, n_comp = parse_ddl_fks(ddl)
    assert fks == [("child", ["pid"], "parent", ["id"]), ("child", ["a", "b"], "other", ["x", "y"])]
    assert n_comp == 1
    # constraint lines must not leak in as columns
    assert cols(metadata_from_ddl(ddl), "child") == ["id", "code", "a", "b", "pid"]


def test_13_one_line_ddl_robust_vs_legacy():
    ddl = "CREATE TABLE t (a int, b int, PRIMARY KEY (a), UNIQUE (b));"
    assert cols(metadata_from_ddl(ddl), "t") == ["a", "b"]
    assert cols(metadata_from_ddl(ddl, legacy=True), "t") == ["a"]  # vendored: one "line" -> one column


# extras --------------------------------------------------------------------
def test_empty_and_blank_ddl():
    for ddl in ("", "   \n", None):
        meta = metadata_from_ddl(ddl, database="db")
        assert meta == {"database": "db", "tables": [], "columns_by_table": {}}
        assert list(iter_ddl_table_bodies(ddl)) == []
        assert parse_ddl_fks(ddl or "") == ([], 0)
        assert parse_ddl_primary_unique(ddl or "") == ([], [])


def test_comments_with_parens_and_keywords_are_ignored():
    ddl = (
        "-- schema (draft\nCREATE TABLE t (\n  a int, -- note: (unbalanced\n  /* b int PRIMARY KEY */\n  c text\n);"
    )
    meta = metadata_from_ddl(ddl)
    assert cols(meta, "t") == ["a", "c"]
    assert parse_ddl_primary_unique(ddl)[0] == []


def test_ensure_prediction_metadata_fills_from_ddl_only_when_empty():
    ddl = "CREATE TABLE t (a int);"
    filled = ensure_prediction_metadata({}, ddl, database="d")
    assert filled["tables"] == ["t"] and cols(filled, "t") == ["a"] and filled["database"] == "d"
    given = {"tables": ["x"], "columns_by_table": {"x": [{"COLUMN_NAME": "q"}]}}
    assert ensure_prediction_metadata(given, ddl) == given
    # tables kept when only columns are empty
    kept = ensure_prediction_metadata({"tables": ["keep"], "columns_by_table": {}}, ddl)
    assert kept["tables"] == ["keep"] and cols(kept, "t") == ["a"]


def test_parse_ddl_structured_schema():
    ddl = (
        "CREATE TABLE p (id int PRIMARY KEY);\n"
        "CREATE TABLE c (id int, pid int NOT NULL, PRIMARY KEY (id), FOREIGN KEY (pid) REFERENCES p (id));"
    )
    s = parse_ddl(ddl)
    assert s.table_names() == ["p", "c"]
    c = s.table("c")
    assert c.primary_key == [["id"]]
    assert [(fk.columns, fk.ref_table, fk.ref_columns) for fk in c.foreign_keys] == [(["pid"], "p", ["id"])]
    assert not c.columns[1].nullable


# parser corrections (E0 genuine Domain) ------------------------------------
def test_blob_json_enum_binary_recovered():
    ddl = (
        "CREATE TABLE t (\n"
        "  img BLOB,\n  meta JSON,\n  kind ENUM('a','b'),\n  raw VARBINARY(16),\n  doc LONGTEXT\n);"
    )
    meta = metadata_from_ddl(ddl)
    assert cols(meta, "t") == ["img", "meta", "kind", "raw", "doc"]
    assert col(meta, "t", "img")["DATA_TYPE"] == "blob"
    assert col(meta, "t", "meta")["DATA_TYPE"] == "json"
    assert col(meta, "t", "kind")["DATA_TYPE"] == "enum"
    assert col(meta, "t", "raw")["DATA_TYPE"] == "varbinary"
    assert col(meta, "t", "doc")["DATA_TYPE"] == "longtext"


def test_special_character_identifiers_recovered():
    ddl = (
        "CREATE TABLE t (\n"
        "  Check-in_Time DATETIME,\n"
        "  State/Province VARCHAR(255),\n"
        "  E-book_ID INTEGER NOT NULL\n);"
    )
    meta = metadata_from_ddl(ddl)
    assert cols(meta, "t") == ["Check-in_Time", "State/Province", "E-book_ID"]
    assert col(meta, "t", "E-book_ID")["IS_NULLABLE"] == "NO"


def test_unquoted_apostrophe_does_not_swallow_following_columns():
    ddl = (
        "CREATE TABLE patient (\n"
        "  patient_ID INTEGER PRIMARY KEY,\n"
        "  patient's_treatment_information VARCHAR(255),\n"
        "  registration_category_ID INTEGER,\n"
        "  ward_ID INTEGER\n);"
    )
    meta = metadata_from_ddl(ddl)
    assert cols(meta, "patient") == [
        "patient_ID",
        "patient's_treatment_information",
        "registration_category_ID",
        "ward_ID",
    ]


def test_decimal_and_enum_commas_do_not_split_columns():
    ddl = "CREATE TABLE t (price DECIMAL(10,2) NOT NULL, kind ENUM('a','b','c'), note VARCHAR(10));"
    assert cols(metadata_from_ddl(ddl), "t") == ["price", "kind", "note"]


def test_placeholder_null_type_recovered_without_fabricated_varchar():
    ddl = "CREATE TABLE t (\n  AccountID null PRIMARY KEY,\n  Balance null,\n  Name VARCHAR(255)\n);"
    meta = metadata_from_ddl(ddl)
    assert cols(meta, "t") == ["AccountID", "Balance", "Name"]
    a = col(meta, "t", "AccountID")
    assert a["DATA_TYPE"] == "" and a["TYPE_STATUS"] == "unsupported"
    assert a["COLUMN_KEY"] == "PRI" and a["IS_NULLABLE"] == "NO"
    b = col(meta, "t", "Balance")
    assert b["TYPE_STATUS"] == "unsupported" and b["NULLABILITY_STATUS"] == "unknown"
    assert b["IS_NULLABLE"] == ""
    assert col(meta, "t", "Name")["DATA_TYPE"] == "varchar"


def test_legacy_still_drops_blob():
    ddl = "CREATE TABLE t (a int, b BLOB);"
    assert cols(metadata_from_ddl(ddl, legacy=True), "t") == ["a"]
    assert cols(metadata_from_ddl(ddl, legacy=False), "t") == ["a", "b"]
