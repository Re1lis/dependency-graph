import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from cli import parse_args
from graph import build_graph, package_dependencies, parse_test_graph
from repository import direct_dependencies, find_package, parse_index

ARGUMENT_ERROR = 2


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--repository", "example.org"),
        ("--repository", "ftp://example.org"),
        ("--output", "result.txt"),
        ("--output", "missing-directory/result.svg"),
    ],
)
def test_invalid_options(option, value):
    """Отклоняет неверные адреса и имена выходного файла."""
    args = [
        "--package", "A", "--repository", "https://example.org",
        "--version", "1", "--output", "result.svg", "--max-depth", "2",
    ]
    args[args.index(option) + 1] = value
    with pytest.raises(SystemExit):
        parse_args(args)


def test_invalid_test_file(tmp_path):
    """Отклоняет отсутствующий файл и каталог в тестовом режиме."""
    for path in (tmp_path, tmp_path / "missing.txt"):
        args = [
            "--package", "A", "--repository", str(path), "--test-mode",
            "--version", "1", "--output", "result.svg", "--max-depth", "2",
        ]
        with pytest.raises(SystemExit):
            parse_args(args)


def test_valid_arguments():
    """Проверяет, что корректные аргументы успешно разбираются."""
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

    expected_max_depth = 3

    assert options.package == "curl"
    assert options.max_depth == expected_max_depth


def test_negative_depth_is_rejected():
    """Проверяет отклонение отрицательной максимальной глубины."""
    with pytest.raises(SystemExit) as error:
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
    assert error.value.code == ARGUMENT_ERROR


def test_index_parsing_and_direct_dependencies():
    """Проверяет разбор записи APKINDEX и списка зависимостей."""
    index = "P:curl\nV:1.0-r0\nD:libcurl zlib\n\nP:zlib\nV:2.0-r0\n"
    package = find_package(parse_index(index), "curl", "1.0-r0")
    assert direct_dependencies(package) == ["libcurl", "zlib"]


def test_recursive_bfs_and_depth():
    """Проверяет рекурсивный BFS и ограничение глубины."""
    graph = parse_test_graph("A: B C\nB: D\nC: D\nD: E\nE:")
    result = build_graph(graph, "A", max_depth=2)
    assert result["A"] == ["B", "C"]
    assert result["B"] == ["D"]
    assert result["C"] == ["D"]
    assert "E" not in result


def test_filter():
    """Проверяет исключение пакета по подстроке."""
    graph = parse_test_graph("A: B debug-lib\nB: A\ndebug-lib:")
    result = build_graph(graph, "A", max_depth=5, filter_text="debug")
    assert result == {"A": ["B"], "B": ["A"]}


def test_cycle_graph():
    """Проверяет сохранение циклического ребра без бесконечного обхода."""
    graph = parse_test_graph("A: B\nB: A")
    assert build_graph(graph, "A", 5) == {"A": ["B"], "B": ["A"]}


def test_alpine_dependency_resolution():
    """Проверяет версию и разрешение so:libz.so.1 через поле p пакета zlib."""
    packages = parse_index(
        "P:curl\nV:1.0\nD:libcurl=1.0 so:libz.so.1\n"
        "p:cmd:curl=1.0\n\n"
        "P:libcurl\nV:1.0\nD:zlib\n\n"
        "P:zlib\nV:1.0\np:so:libz.so.1\n"
    )
    graph = package_dependencies(packages)
    assert graph["curl"] == ["libcurl", "zlib"]
    assert graph["libcurl"] == ["zlib"]
