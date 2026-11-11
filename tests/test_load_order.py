"""Проверки порядка загрузки на тестовых графах."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from graph import build_graph, parse_test_graph
from load_order import DependencyCycleError, load_order

LEVEL_COUNT = 200


def test_shared_dependency_loads_once_and_first():
    """Общая зависимость загружается перед обоими пакетами."""
    source = parse_test_graph("A: B C\nB: D\nC: D\nD:")
    graph = build_graph(source, "A", max_depth=2)
    assert load_order(graph) == ["D", "B", "C", "A"]


def test_chain_order():
    """Цепочка выводится от глубокой зависимости к корню."""
    graph = build_graph(parse_test_graph("A: B\nB: C\nC:"), "A", 2)
    assert load_order(graph) == ["C", "B", "A"]


def test_many_levels():
    """Обход проходит цепочку из двухсот уровней."""
    graph = {str(i): [str(i + 1)] for i in range(LEVEL_COUNT)}
    graph[str(LEVEL_COUNT)] = []
    result = build_graph(graph, "0", LEVEL_COUNT)
    expected_count = LEVEL_COUNT + 1
    assert len(result) == expected_count


def test_depth_limit_changes_order():
    """За пределами глубины зависимости не попадают в порядок."""
    source = parse_test_graph("A: B\nB: C\nC:")
    graph = build_graph(source, "A", max_depth=1)
    assert load_order(graph) == ["B", "A"]


def test_cycle_has_no_load_order():
    """При цикле программа сообщает об отсутствии порядка."""
    source = parse_test_graph("A: B\nB: A")
    graph = build_graph(source, "A", max_depth=3)
    with pytest.raises(DependencyCycleError, match="цикл"):
        load_order(graph)
