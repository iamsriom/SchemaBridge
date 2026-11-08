import pytest

from src.normalization import (
    normalize_ddl,
    normalize_identifier,
    normalize_rschema_name,
    type_family,
    types_compatible,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Users", "users"),
        ("  `Users`  ", "users"),
        ('"Order Items"', "order items"),
        ("[Dbo]", "dbo"),
        ("'x'", "x"),
        ("`a``b`", "a`b"),
        ('"say ""hi"""', 'say "hi"'),
        ("", ""),
        (None, ""),
        ("no_quotes", "no_quotes"),
        ("`unbalanced", "`unbalanced"),
    ],
)
def test_normalize_identifier(raw, expected):
    assert normalize_identifier(raw) == expected


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Airplane Number", "airplanenumber"),
        ("airplane_number", "airplanenumber"),
        ("airplane-number", "airplanenumber"),
        ("Airplanes", "airplane"),  # trailing s dropped
        ("address", "address"),  # 'ss' kept
        ("bus", "bus"),  # too short (len<=3) to strip
        ("FamilyMembers", "family"),  # suffix 'members' removed
        ("order_details", "order"),
        ("record", "record"),  # stem too short after removal -> unchanged
        ("StudentRecords", "student"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_rschema_name(raw, expected):
    assert normalize_rschema_name(raw) == expected


def test_rschema_matches_gold_and_prediction_spellings():
    assert normalize_rschema_name("Airplane Number") == normalize_rschema_name("airplane_numbers")


def test_strict_and_rschema_normalizers_differ():
    assert normalize_identifier("Airplanes") != normalize_identifier("airplane")
    assert normalize_rschema_name("Airplanes") == normalize_rschema_name("airplane")


@pytest.mark.parametrize(
    "dtype,family",
    [
        ("INT", "int"), ("integer", "int"), ("bigint", "int"), ("tinyint", "int"),
        ("varchar", "str"), ("CHAR", "str"), ("text", "str"),
        ("decimal", "decimal"), ("datetime", "datetime"), ("", ""), (None, ""),
    ],
)
def test_type_family(dtype, family):
    assert type_family(dtype) == family


def test_types_compatible_families():
    assert types_compatible("int", "bigint")
    assert types_compatible("varchar", "text")
    assert not types_compatible("int", "varchar")
    assert not types_compatible("decimal", "float")
    assert types_compatible("date", "DATE")


def test_types_compatible_legacy_does_not_know_integer():
    assert types_compatible("int", "integer")  # robust
    assert not types_compatible("int", "integer", legacy=True)  # vendored quirk, documented


def test_normalize_ddl_drops_comments_and_whitespace():
    ddl = "-- hi\nCREATE   TABLE T (\n  A INT\n);\n\n"
    assert normalize_ddl(ddl) == "create table t ( a int );"
