from cli import parse_args


def main() -> None:
    """Выводит настройки первого этапа."""
    options = parse_args()
    print(f"package={options.package}")
    print(f"repository={options.repository}")
    print(f"test_mode={options.test_mode}")
    print(f"version={options.version}")
    print(f"output={options.output}")
    print(f"ascii_tree={options.ascii_tree}")
    print(f"max_depth={options.max_depth}")
    print(f"filter={options.filter}")


if __name__ == "__main__":
    main()
