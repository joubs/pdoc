import warnings

import pytest
from pathlib import Path
from unittest.mock import call, patch

from pdoc import pdoc
from pdoc.__main__ import cli, _nicer_showwarning

here = Path(__file__).parent


def test_cli(tmp_path):
    cli([str(here / "testdata" / "demo_long.py"), "-o", str(tmp_path)])
    assert (tmp_path / "demo_long.html").read_text().startswith("<!doctype html>")
    assert (tmp_path / "index.html").read_text().startswith("<!doctype html>")

    with pytest.raises(SystemExit, match="1"):
        cli([])


def test_cli_version(capsys):
    cli(["--version"])
    assert "pdoc:" in capsys.readouterr().out


def test_cli_web(monkeypatch):
    with patch("pdoc.web.open_browser") as open_browser:
        with patch(
            "pdoc.web.DocServer.serve_forever", side_effect=KeyboardInterrupt
        ) as serve_forever:
            cli([str(here / "testdata" / "demopackage" / "_child_d.py")])
            assert open_browser.call_args == call(
                "http://localhost:8080/demopackage/_child_d.html"
            )
            assert serve_forever.call_args == call()


def test_api(tmp_path):
    assert pdoc(here / "testdata" / "demo_long.py").startswith("<!doctype html>")
    with pytest.raises(ValueError, match="Invalid rendering format"):
        assert pdoc(here / "testdata" / "demo_long.py", format="invalid")
    with pytest.raises(ValueError, match="Module not found"):
        with pytest.warns(UserWarning, match="Cannot find spec"):
            assert pdoc(
                here / "notfound.py",
            )

    # temporarily insert syntax error - we don't leave it permanently to not confuse mypy, flake8 and black.
    (here / "syntax_err" / "syntax_err.py").write_bytes(b"class")
    with pytest.warns(
        UserWarning, match="Error importing test.syntax_err.syntax_err"
    ):
        pdoc(here / "syntax_err", output_directory=tmp_path)
    (here / "syntax_err" / "syntax_err.py").write_bytes(
        b"# syntax error will be inserted by test here\n"
    )


def test_patch_showwarnings(capsys, monkeypatch):
    monkeypatch.setattr(warnings, "showwarning", _nicer_showwarning)

    warnings.warn("test")
    assert capsys.readouterr().err.startswith("Warn: test (")

    warnings.warn("test", RuntimeWarning)
    assert capsys.readouterr().err == "Warn: test\n"

    warnings.warn("test", SyntaxWarning)
    assert capsys.readouterr().err.startswith("SyntaxWarning: test (")
