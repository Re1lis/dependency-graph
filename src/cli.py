import argparse
from pathlib import Path
from urllib.parse import urlsplit

MIN_DEPTH = 0


def add_load_order_option(parser: argparse.ArgumentParser) -> None:
    """Добавляет переключатель вывода порядка загрузки."""
    parser.add_argument(
        "--load-order", action="store_true", help="показать порядок загрузки"
    )


def build_parser() -> argparse.ArgumentParser:
    """Создаёт и настраивает парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Настройка анализа зависимостей Alpine-пакетов"
    )
    parser.add_argument(
        "--package", required=True, help="имя анализируемого пакета"
    )
    parser.add_argument(
        "--repository",
        required=True,
        help="URL репозитория или путь к тестовому файлу",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="использовать локальный тестовый репозиторий",
    )
    parser.add_argument("--version", required=True, help="версия пакета")
    add_load_order_option(parser)
    parser.add_argument(
        "--output", required=True, help="имя выходного SVG-файла"
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="включить вывод ASCII-дерева",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        required=True,
        help="максимальная глубина анализа",
    )
    parser.add_argument(
        "--filter",
        default="",
        help="подстрока для исключения пакетов",
    )
    return parser


def parse_args(args=None):
    """Разбирает аргументы запуска и проверяет их значения.

    Возвращает объект с настройками программы или завершает запуск
    с сообщением об ошибке, если параметры некорректны.
    """
    parser = build_parser()
    options = parser.parse_args(args)

    if not options.package.strip():
        parser.error("параметр --package не может быть пустым")
    if not options.repository.strip():
        parser.error("параметр --repository не может быть пустым")
    if options.test_mode:
        if not Path(options.repository).is_file():
            parser.error(
                "--repository: тестовый файл не найден или это каталог"
            )
    else:
        url = urlsplit(options.repository)
        if url.scheme not in ("http", "https") or not url.netloc:
            parser.error(
                "--repository: укажите полный URL с http:// или https://"
            )
    if not options.version.strip():
        parser.error("параметр --version не может быть пустым")
    output_is_invalid = (
        not options.output.strip()
        or not options.output.lower().endswith(".svg")
    )
    if output_is_invalid:
        parser.error(
            "параметр --output должен содержать непустое имя .svg-файла"
        )
    output = Path(options.output)
    if not output.stem or not output.parent.is_dir():
        parser.error("--output: укажите имя файла и существующий каталог")
    if options.max_depth < MIN_DEPTH:
        parser.error("параметр --max-depth должен быть неотрицательным")
    return options
