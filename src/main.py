from pathlib import Path

from cli import parse_args
from graph import (
    build_graph,
    format_graph,
    package_dependencies,
    parse_test_graph,
)
from load_order import DependencyCycleError, load_order
from repository import (
    RepositoryError,
    find_package,
    load_index,
    parse_index,
)


def main() -> None:
    """Выводит граф и порядок загрузки зависимостей пакета."""
    options = parse_args()

    try:
        if options.test_mode:
            graph_data = parse_test_graph(
                Path(options.repository).read_text(encoding="utf-8")
            )
        else:
            index_text = load_index(options.repository)
            packages = parse_index(index_text)
            package = find_package(packages, options.package, options.version)
            other_packages = [
                item for item in packages if item["P"] != options.package
            ]
            graph_data = package_dependencies(other_packages + [package])
    except RepositoryError as error:
        raise SystemExit(f"error: {error}") from error
    except (OSError, UnicodeDecodeError) as error:
        raise SystemExit(f"error: не удалось прочитать тестовый граф: {error}")

    graph = build_graph(
        graph_data, options.package, options.max_depth, options.filter
    )

    if not options.load_order:
        print(f"\nГраф зависимостей пакета {options.package}:")
        print(format_graph(graph))
        return

    try:
        order = load_order(graph)
    except DependencyCycleError as error:
        raise SystemExit(f"Порядок загрузки не определён: {error}") from error
    else:
        print("\nПорядок загрузки зависимостей:")
        for name in order:
            print(name)


if __name__ == "__main__":
    main()
