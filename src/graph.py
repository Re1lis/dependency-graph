"""Построение графа зависимостей на третьем этапе."""

import re


def dependency_name(dependency: str) -> str:
    """Извлекает имя пакета из записи с ограничением версии."""
    return re.split(
        r"[<>=~]", dependency, maxsplit=1
    )[0]


def package_dependencies(
    packages: list[dict[str, str]],
) -> dict[str, list[str]]:
    """Создаёт отображение имени пакета на имена его зависимостей."""
    return {
        package["P"]: [
            dependency_name(item) for item in package.get("D", "").split()
        ]
        for package in packages
        if package.get("P")
    }


def parse_test_graph(graph_text: str) -> dict[str, list[str]]:
    """Разбирает тестовый граф в формате `A: B C`.

    Пустая правая часть означает, что у пакета нет зависимостей.
    """
    graph = {}
    for line in graph_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        package, raw_dependencies = line.split(":", maxsplit=1)
        graph[package.strip()] = raw_dependencies.split()
    return graph


def build_graph(
    dependencies: dict[str, list[str]],
    root: str,
    max_depth: int,
    filter_text: str = "",
) -> dict[str, list[str]]:
    """Строит граф зависимостей рекурсивным BFS-обходом.

    Обход останавливается на максимальной глубине, пропускает пакеты,
    содержащие фильтр, и не посещает один пакет повторно.
    """
    result = {root: []}
    visited = {root}
    queue = [(root, 0)]

    def visit_queue() -> None:
        """Рекурсивно обрабатывает очередь BFS по уровням глубины."""
        if not queue:
            return
        package, depth = queue.pop(0)
        if depth < max_depth:
            for dependency in dependencies.get(package, []):
                if filter_text and filter_text in dependency:
                    continue
                result.setdefault(package, []).append(dependency)
                result.setdefault(dependency, [])
                if dependency not in visited:
                    visited.add(dependency)
                    queue.append((dependency, depth + 1))
        visit_queue()

    visit_queue()
    return result


def format_graph(graph: dict[str, list[str]]) -> str:
    """Форматирует граф в удобный для вывода список связей."""
    lines = []
    for package, dependencies in graph.items():
        if dependencies:
            lines.append(f"{package} -> {', '.join(dependencies)}")
        else:
            lines.append(f"{package} -> (нет зависимостей)")
    return "\n".join(lines)
