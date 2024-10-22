from collections import defaultdict

from xerparser.schemas.task import TASK, LinkToTask


def find_redundant_logic(task: TASK) -> list[list[LinkToTask]]:
    redundant_paths = []

    for pred in task.predecessors:
        if pred_paths := _search_redundant_paths(pred, task, [pred], set()):
            redundant_paths.extend(pred_paths)

    return redundant_paths


def _search_redundant_paths(
    task_pred: LinkToTask,
    epoch_task: TASK,
    path: list[LinkToTask],
    mem: set[TASK],
):
    paths = []
    # Work in progress - group paths by redundant predecessor
    dict_paths = defaultdict(list)
    for pred in task_pred.task.predecessors:
        if pred.task.type.is_loe:
            continue

        if pred in epoch_task.predecessors:
            if (
                all(
                    (p.link[0] == pred.link[0]) or (p.link[1] == pred.link[1])
                    for p in [pred] + path
                )
                and pred.link[1] == path[-1].link[1]
            ):
                paths.append([pred] + path)
                index = epoch_task.predecessors.index(pred)
                dict_paths[epoch_task.predecessors[index]].append([pred] + path)

        if pred.task in mem:
            continue
        if new_paths := _search_redundant_paths(pred, epoch_task, [pred] + path, mem):
            paths.extend(new_paths)
        mem.add(pred.task)
    return paths
