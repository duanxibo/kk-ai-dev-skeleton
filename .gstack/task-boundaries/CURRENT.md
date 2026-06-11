# Current Task Boundary Entry

This shared file is a stable entry document. It is not a shared active-task pointer.

Use `.gstack/task-boundaries/CURRENT.local.md` or `KK_ACTIVE_BOUNDARY` for local active task state.

## How To Use

1. Start a task with `kk-task-kickoff`.
2. Create or update a concrete boundary under `.gstack/task-boundaries/`.
3. Set the local active boundary with:

```bash
bash .gstack/scripts/use_boundary.sh .gstack/task-boundaries/<boundary>.md
```

## Rule

Do not commit machine-specific active task state.

