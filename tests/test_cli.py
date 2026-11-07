import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from cli import parse_args


def test_valid_arguments():
    """Проверяет корректные параметры."""
    options = parse_args(
        [
            "--package",
            "curl",
            "--repository",
            "https://example.org/repo",
            "--version",
            "1.0-r0",
            "--output",
            "result.svg",
            "--max-depth",
            "3",
        ]
    )
    assert options.package == "curl"
    assert options.max_depth == 3


def test_negative_depth_is_rejected():
    """Проверяет ошибку отрицательной глубины."""
    try:
        parse_args(
            [
                "--package",
                "curl",
                "--repository",
                "https://example.org/repo",
                "--version",
                "1.0-r0",
                "--output",
                "result.svg",
                "--max-depth",
                "-1",
            ]
        )
    except SystemExit as error:
        assert error.code == 2
    else:
        raise AssertionError("Ожидалась ошибка для отрицательной глубины")
