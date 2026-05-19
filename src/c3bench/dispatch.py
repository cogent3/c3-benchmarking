"""CLI dispatcher invoked by hyperfine: imports one tool's deps, calls it.

Each `(task, tool)` pair becomes a standalone process invocation. The orchestrator
(`c3bench <task>`) writes shell-command templates that funnel through this entry
point, e.g. `c3bench-run parse-fasta bp --path X`.

The function's return value is discarded — hyperfine measures wall time and peak
RSS of the whole process, which is the metric we want.
"""

import importlib
import pathlib

import click

TASK_MODULES = {
    "parse-fasta": "c3bench.parse_fa",
    "parse-gbk": "c3bench.parse_gbk",
    "parse-ann-gff": "c3bench.parse_ann_gff",
    "load-aln": "c3bench.load_aln",
}


@click.command(context_settings={"show_default": True})
@click.argument("task", type=click.Choice(list(TASK_MODULES)))
@click.argument("tool")
@click.option("--path", type=pathlib.Path, required=True)
def main(task: str, tool: str, path: pathlib.Path) -> None:
    """Run a single (task, tool) pair against `path`."""
    module = importlib.import_module(TASK_MODULES[task])
    func = getattr(module, tool)
    func(path)


if __name__ == "__main__":
    main()
