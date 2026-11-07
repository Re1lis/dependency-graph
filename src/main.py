from cli import parse_args
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
        index_text = load_index(options.repository, options.test_mode)
        package = find_package(
            parse_index(index_text), options.package, options.version
        )
    except RepositoryError as error:
        raise SystemExit(f"error: {error}") from error

    print(f"\nПрямые зависимости пакета {options.package}:")
    dependencies = direct_dependencies(package)
    for dependency in dependencies or ["отсутствуют"]:
        print(f"- {dependency}")


if __name__ == "__main__":
    main()
