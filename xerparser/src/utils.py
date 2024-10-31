from xerparser.schemas.task import TASK, LinkToTask


def find_redundant_logic(task: TASK) -> list[list[LinkToTask]]:
    redundant_paths = []

    for pred in task.predecessors:
        path = [pred]
        mem = set()
        if paths := _search_redundant_paths(pred, task, path, mem):
            redundant_paths.extend(paths)

    return redundant_paths


def _search_redundant_paths(
    task_pred: LinkToTask,
    epoch_task: TASK,
    path: list[LinkToTask],
    mem: set[TASK],
):
    paths = []

    for pred in task_pred.task.predecessors:
        if pred.task.type.is_loe:
            continue

        if _is_valid_path(epoch_task.predecessors, pred, path):
            paths.append([pred] + path)

        if pred.task in mem:
            continue

        if new_paths := _search_redundant_paths(pred, epoch_task, [pred] + path, mem):
            paths.extend(new_paths)

        mem.add(pred.task)
    return paths


def _is_valid_path(
    epoch_preds: list[LinkToTask], pred: LinkToTask, path: list[LinkToTask]
) -> bool:
    if pred not in epoch_preds:
        return False
    if not all(
        (p.link[0] == pred.link[0]) or (p.link[1] == pred.link[1])
        for p in [pred] + path
    ):
        return False

    return pred.link[1] == path[-1].link[1]
