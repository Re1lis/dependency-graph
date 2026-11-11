"""Порядок загрузки пакетов по построенному графу зависимостей."""


class DependencyCycleError(ValueError):
    """Порядок загрузки невозможно определить из-за цикла."""


def load_order(graph: dict[str, list[str]]) -> list[str]:
    """Возвращает порядок: зависимости раньше использующих их пакетов.

    При цикле вызывает DependencyCycleError. Порядок между независимыми
    пакетами соответствует порядку их появления в графе.
    """
    pending = {name: set(deps) for name, deps in graph.items()}
    order = []
    while pending:
        ready = [name for name, deps in pending.items() if not deps]
        if not ready:
            names = ", ".join(pending)
            raise DependencyCycleError(f"цикл зависимостей: {names}")
        for name in ready:
            order.append(name)
            del pending[name]
        for deps in pending.values():
            deps.difference_update(ready)
    return order
