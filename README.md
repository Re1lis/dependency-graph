# Dependency Graph

Консольное приложение для анализа зависимостей пакетов Alpine Linux.

## Первый этап

На первом этапе приложение принимает параметры командной строки, проверяет их
и выводит в формате `ключ=значение`. Работа с репозиторием и построение графа
будут добавлены на следующих этапах.

## Запуск

```text
run.bat --package curl --repository https://dl-cdn.alpinelinux.org/alpine/v3.24/main/x86_64/ --version 8.17.0-r1 --output curl.svg --max-depth 3 --filter debug --ascii-tree
```
