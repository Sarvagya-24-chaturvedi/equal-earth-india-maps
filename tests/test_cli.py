"""Tests for the command-line interface execution and argument parsing."""

import pytest
from pathlib import Path
from equal_earth.cli import main


def test_cli_help(capsys):
    """Test CLI top-level help execution."""
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "Equal Earth India Maps Toolkit" in captured.out


def test_cli_project_benchmark(capsys):
    """Test CLI benchmark command."""
    exit_code = main(["project", "--benchmark"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "[✓] All reference benchmark comparisons verified." in captured.out


def test_cli_project_forward_inverse(capsys):
    """Test forward and inverse transforms via CLI."""
    exit_code_fwd = main(["project", "--forward", "78.0", "20.0"])
    assert exit_code_fwd == 0
    captured_fwd = capsys.readouterr()
    assert "7264273.592" in captured_fwd.out

    exit_code_inv = main(["project", "--inverse", "7264273.592", "2556518.151"])
    assert exit_code_inv == 0
    captured_inv = capsys.readouterr()
    assert "78.000000" in captured_inv.out


def test_cli_india_command(tmp_path):
    """Test CLI generation of India administrative map."""
    out_file = tmp_path / "cli_india.png"
    exit_code = main(["india", "--theme", "academic_clean", "--dpi", "80", "-o", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()


def test_cli_india_choropleth_sample(tmp_path):
    """Test CLI generation of India choropleth from sample dataset."""
    out_file = tmp_path / "cli_choropleth.png"
    exit_code = main(["india", "--choropleth", "literacy", "--dpi", "80", "-o", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()


def test_cli_global_command(tmp_path):
    """Test CLI generation of global map centered on India."""
    out_file = tmp_path / "cli_global.png"
    exit_code = main(["global", "--center-lon", "78.0", "--dpi", "80", "-o", str(out_file)])
    assert exit_code == 0
    assert out_file.exists()
