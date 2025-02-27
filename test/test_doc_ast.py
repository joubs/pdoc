import pytest
import types

from pdoc import doc_ast
from pdoc.doc_ast import _dedent, _parse, type_checking_sections


def test_dedent():
    # not indented
    assert _dedent("def foo(): pass") == "def foo(): pass"

    # indented
    assert (
        _dedent(
            """\
    def foo():
        pass"""
        )
        == "def foo():\n        pass"
    )

    # with decorator
    assert (
        _dedent(
            """\
    @foo
    def foo():
        pass"""
        )
        == "@foo\ndef foo():\n        pass"
    )

    # with decorator and comment
    assert (
        _dedent(
            """\
    @foo
    # hello world
    def foo():
        pass"""
        )
        == "@foo\n# hello world\ndef foo():\n        pass"
    )


def test_parse_error():
    with pytest.warns(UserWarning, match="Error parsing source code"):
        assert _parse("!!!")


@pytest.mark.parametrize("code,statements", [
    ("""import typing\nif typing.TYPE_CHECKING:\n\tprint(42)""", 1),
    ("""from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n\tprint(42)\n\tprint(43)""", 2),
    ("""print(1234)""", 0),
])
def test_type_checking_sections(code, statements, monkeypatch):
    monkeypatch.setattr(doc_ast, "get_source", lambda _: code)
    assert len(type_checking_sections(types.ModuleType("test_type_checking_sections")).body) == statements
