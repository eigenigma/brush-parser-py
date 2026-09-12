"""Variant classes behave as pyo3 complex-enum subclasses across the surface."""

import inspect

import pytest

from brush_parser import _core as core
from tests.test_registry import AST_CLASSES, WORD_CLASSES

SIMPLE_ENUMS = {
    "SeparatorOperator",
    "ProcessSubstitutionKind",
    "IoFileRedirectKind",
    "CaseItemPostAction",
    "UnaryPredicate",
    "BinaryPredicate",
    "ParameterTestType",
    "SubstringMatchKind",
}


def variant_classes(cls: type) -> list[type]:
    return [
        attribute
        for attribute in vars(cls).values()
        if inspect.isclass(attribute) and issubclass(attribute, cls)
    ]


def enum_classes() -> list[type]:
    return [
        getattr(core, name)
        for name in sorted(AST_CLASSES | WORD_CLASSES)
        if variant_classes(getattr(core, name))
    ]


@pytest.mark.parametrize("cls", enum_classes(), ids=lambda cls: cls.__name__)
def test_every_variant_is_a_final_subclass_with_match_args(cls):
    for variant in variant_classes(cls):
        assert variant.__qualname__ == f"{cls.__name__}.{variant.__name__}"
        assert variant.__module__ == "brush_parser._core"
        assert isinstance(vars(variant)["__match_args__"], tuple)
        assert variant.__hash__ is None
        with pytest.raises(TypeError):
            type("Sub", (variant,), {})


@pytest.mark.parametrize("cls", enum_classes(), ids=lambda cls: cls.__name__)
def test_base_class_cannot_be_instantiated(cls):
    with pytest.raises(TypeError):
        cls()


@pytest.mark.parametrize("name", sorted(SIMPLE_ENUMS))
def test_simple_enum_members_are_instances(name):
    cls = getattr(core, name)
    members = {
        attribute: value
        for attribute, value in vars(cls).items()
        if not attribute.startswith("_") and isinstance(value, cls)
    }
    assert members
    for attribute, member in members.items():
        assert member == getattr(cls, attribute)
        assert member.__hash__ is None
    assert len({repr(member) for member in members.values()}) == len(members)


def test_isinstance_after_construction_and_parsing():
    built = core.AndOr.And(core.Pipeline(None, bang=False, seq=()))
    assert isinstance(built, core.AndOr)
    assert isinstance(built, core.AndOr.And)
    assert not isinstance(built, core.AndOr.Or)
    parsed = core.parse_program("a && b").complete_commands[0].items[0]
    assert isinstance(parsed.list.additional[0], core.AndOr.And)


def test_match_positional_and_keyword_patterns():
    node = core.IoRedirect.File(
        2,
        core.IoFileRedirectKind.DuplicateOutput,
        core.IoFileRedirectTarget.Duplicate(core.Word("1", None)),
    )
    match node:
        case core.IoRedirect.File(fd, kind, core.IoFileRedirectTarget.Duplicate(word)):
            assert (fd, kind, word.value) == (
                2,
                core.IoFileRedirectKind.DuplicateOutput,
                "1",
            )
        case _:
            pytest.fail("positional pattern did not match")
    match node:
        case core.IoRedirect.File(target=core.IoFileRedirectTarget.Duplicate(word=w)):
            assert w.value == "1"
        case _:
            pytest.fail("keyword pattern did not match")


def test_empty_variants_match_and_compare():
    assert core.TildeExpr.Home() == core.TildeExpr.Home()
    assert core.TildeExpr.Home() != core.TildeExpr.WorkingDir()
    match core.TildeExpr.Home():
        case core.TildeExpr.Home():
            pass
        case _:
            pytest.fail("empty variant did not match")
