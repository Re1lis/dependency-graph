"""Работа с индексом пакетов Alpine Linux для второго этапа."""

import io
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

MIN_FIELD_LINE_LENGTH = 2


class RepositoryError(RuntimeError):
    """Ошибка загрузки или разбора индекса пакетов."""


def load_index(repository: str) -> str:
    """Загружает APKINDEX из URL репозитория или локального файла.

    Возвращает текстовый индекс, содержащий записи пакетов Alpine Linux.
    """
    source = repository.strip()
    try:
        if not source.startswith(("http://", "https://")):
            data = Path(source).read_bytes()
        else:
            request = urllib.request.Request(
                source.rstrip("/") + "/APKINDEX.tar.gz",
                headers={"User-Agent": "dependency-graph/1.0"},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
    except (OSError, urllib.error.URLError) as error:
        message = f"не удалось загрузить индекс: {error}"
        raise RepositoryError(message) from error

    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            index_file = next(
                (
                    item
                    for item in archive.getmembers()
                    if item.isfile() and Path(item.name).name == "APKINDEX"
                ),
                None,
            )
            if index_file is None:
                raise RepositoryError("архив индекса пуст")
            extracted = archive.extractfile(index_file)
            if extracted is None:
                raise RepositoryError("не удалось прочитать APKINDEX")
            return extracted.read().decode("utf-8")
    except (OSError, UnicodeDecodeError, tarfile.TarError) as error:
        message = f"не удалось разобрать APKINDEX: {error}"
        raise RepositoryError(message) from error


def parse_index(index_text: str) -> list[dict[str, str]]:
    """Преобразует текст APKINDEX в список словарей с полями пакетов."""
    packages = []
    for block in index_text.strip().split("\n\n"):
        fields = {}
        for line in block.splitlines():
            if len(line) >= MIN_FIELD_LINE_LENGTH and line[1] == ":":
                fields[line[0]] = line[2:].strip()
        if fields.get("P") and fields.get("V"):
            packages.append(fields)
    return packages


def find_package(packages, package_name: str, version: str):
    """Находит пакет по точному имени и версии.

    Вызывает RepositoryError, если подходящая запись отсутствует.
    """
    for package in packages:
        if package.get("P") == package_name and package.get("V") == version:
            return package
    raise RepositoryError(
        f"пакет '{package_name}' версии '{version}' не найден в индексе"
    )


def direct_dependencies(package) -> list[str]:
    """Возвращает список прямых зависимостей из записи пакета."""
    return package.get("D", "").split()
