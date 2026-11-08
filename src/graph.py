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
    """Создаёт отображение пакета на разрешённые имена зависимостей.

    Поле `D` может содержать версию или capability `so:...`. Поле `p`
    показывает, какой пакет предоставляет такую capability.
    """
    package_names = {package.get("P") for package in packages}
    providers = {}
    for package in packages:
        package_name = package.get("P")
        for provided in package.get("p", "").split():
            providers[dependency_name(provided)] = package_name

    return {
        package["P"]: [
            resolve_dependency(item, package_names, providers)
            for item in package.get("D", "").split()
        ]
        for package in packages
        if package.get("P")
    }


def resolve_dependency(
    dependency: str,
    package_names: set[str],
    providers: dict[str, str],
) -> str:
    """Преобразует запись зависимости в имя пакета для обхода графа."""
    name = dependency_name(dependency)
    if name in package_names:
        return name
    return providers.get(name, name)


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

    def visit_level(level: list[str], depth: int) -> None:
        """Обрабатывает один уровень BFS и переходит к следующему."""
        if not level or depth >= max_depth:
            return
        next_level = []
        for package in level:
            for dependency in dependencies.get(package, []):
                if filter_text and filter_text in dependency:
                    continue
                result.setdefault(package, [])
                if dependency in result[package]:
                    continue
                result[package].append(dependency)
                result.setdefault(dependency, [])
                if dependency not in visited:
                    visited.add(dependency)
                    next_level.append(dependency)
        visit_level(next_level, depth + 1)

    visit_level([root], 0)
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
