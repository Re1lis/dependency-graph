from pathlib import Path

from cli import parse_args
from graph import (
    build_graph,
    format_graph,
    package_dependencies,
    parse_test_graph,
)
from repository import (
    RepositoryError,
    find_package,
    load_index,
    parse_index,
)


def main() -> None:
    """Строит граф зависимостей выбранного пакета."""
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
            others = [item for item in packages if item["P"] != options.package]
            graph_data = package_dependencies(others + [package])
    except RepositoryError as error:
        raise SystemExit(f"error: {error}") from error
    except (OSError, UnicodeDecodeError) as error:
        raise SystemExit(f"error: не удалось прочитать тестовый граф: {error}")

    graph = build_graph(
        graph_data, options.package, options.max_depth, options.filter
    )

    print(f"\nГраф зависимостей пакета {options.package}:")
    print(format_graph(graph))


if __name__ == "__main__":
    main()
