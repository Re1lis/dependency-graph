from cli import parse_args
from graph import build_graph, format_graph, parse_test_graph
from repository import (
    RepositoryError,
    direct_dependencies,
    find_package,
    load_index,
    parse_index,
)


def main() -> None:
    """Запускает программу второго этапа и выводит прямые зависимости пакета."""
    options = parse_args()
    try:
        if options.test_mode:
            from pathlib import Path

            graph_data = parse_test_graph(
                Path(options.repository).read_text(encoding="utf-8")
            )
        else:
            index_text = load_index(options.repository)
            packages = parse_index(index_text)
            package = find_package(packages, options.package, options.version)
            graph_data = {
                item["P"]: direct_dependencies(item) for item in packages
            }
            graph_data[options.package] = direct_dependencies(package)
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
