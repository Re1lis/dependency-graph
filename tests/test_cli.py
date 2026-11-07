import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from cli import parse_args
from repository import direct_dependencies, find_package, parse_index


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


def test_index_parsing_and_direct_dependencies():
    """Проверяет разбор записи APKINDEX и списка зависимостей."""
    index = "P:curl\nV:1.0-r0\nD:libcurl zlib\n\nP:zlib\nV:2.0-r0\n"
    package = find_package(parse_index(index), "curl", "1.0-r0")
    assert direct_dependencies(package) == ["libcurl", "zlib"]
