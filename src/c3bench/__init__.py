"""c3bench: Benchmarking suite for sequence analysis tools."""

import importlib
import json
import math
import pathlib
import shlex
import statistics
import subprocess
import tempfile

import click
import cogent3

__version__ = "0.1"


_click_command_opts = {
    "no_args_is_help": True,
    "context_settings": {"show_default": True},
}


# Maps the user-facing task name (the click subcommand) to (module_path,
# results-subdirectory name).
_TASK_MODULES = {
    "parse-fasta": ("c3bench.parse_fa", "parse_fasta"),
    "parse-gbk": ("c3bench.parse_gbk", "parse_gbk"),
    "parse-gff": ("c3bench.parse_gff", "parse_gff"),
    "load-aln": ("c3bench.load_aln", "load_aln"),
}


_TSV_COLUMNS = [
    "Function",
    "Result Type",
    "mean(time) seconds",
    "std(time) seconds",
    "mean(RAM)",
    "std(RAM) bytes",
]


@click.group(**_click_command_opts)
@click.version_option(__version__)
def main() -> None:
    """benchmarking of different tools"""


_path = click.option("--path", type=pathlib.Path, required=True)
_result_root = click.option("--result_root", type=pathlib.Path, required=True)
_runs = click.option("--runs", type=int, default=3)


@main.command(**_click_command_opts)
@click.argument("task", type=click.Choice(list(_TASK_MODULES)))
@_path
def prepare(task: str, path: pathlib.Path) -> None:
    """Build any side-effect artifacts a task needs before timing.

    Idempotent: re-running is safe. Task modules without a `prepare` function
    are a no-op.
    """
    module_name, _ = _TASK_MODULES[task]
    module = importlib.import_module(module_name)
    prep = getattr(module, "prepare", None)
    if prep is not None:
        prep(path)


def _stddev(xs: list[float]) -> float:
    return statistics.stdev(xs) if len(xs) >= 2 else 0.0


def _aggregate(result: dict) -> list:
    name = result["command"]
    times = result.get("times") or []
    mems = result.get("memory_usage_byte") or []
    exit_codes = result.get("exit_codes") or []
    failed = any(c != 0 for c in exit_codes)
    if not times:
        return [name, "Error", math.nan, math.nan, math.nan, math.nan]
    status = "Error" if failed else "OK"
    mean_m = statistics.mean(mems) if mems else math.nan
    std_m = _stddev(mems) if mems else math.nan
    return [name, status, statistics.mean(times), _stddev(times), mean_m, std_m]


def _run_task(task: str, path: pathlib.Path, result_root: pathlib.Path, runs: int) -> None:
    module_name, out_subdir = _TASK_MODULES[task]
    module = importlib.import_module(module_name)
    commands: dict[str, str] = module.COMMANDS

    prep = getattr(module, "prepare", None)
    if prep is not None:
        prep(path)

    outdir = result_root / out_subdir / path.parent.name
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = (outdir / f"{path.name}.tsv").absolute()

    quoted_path = shlex.quote(str(path))
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        json_path = pathlib.Path(tmp.name)
    try:
        args = [
            "hyperfine",
            "--warmup", "1",
            "--runs", str(runs),
            "--ignore-failure",
            "--export-json", str(json_path),
        ]
        for tool, template in commands.items():
            args += ["--command-name", tool, template.format(path=quoted_path)]
        subprocess.run(args, check=True)
        data = json.loads(json_path.read_text())
    finally:
        json_path.unlink(missing_ok=True)

    rows = [_aggregate(r) for r in data["results"]]
    table = cogent3.make_table(header=_TSV_COLUMNS, data=rows)
    table.write(outpath)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
def parse_gbk(path: pathlib.Path, result_root: pathlib.Path, runs: int) -> None:
    _run_task("parse-gbk", path, result_root, runs)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
def parse_fasta(path: pathlib.Path, result_root: pathlib.Path, runs: int) -> None:
    _run_task("parse-fasta", path, result_root, runs)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
def parse_gff(path: pathlib.Path, result_root: pathlib.Path, runs: int) -> None:
    _run_task("parse-gff", path, result_root, runs)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
def load_aln(path: pathlib.Path, result_root: pathlib.Path, runs: int) -> None:
    _run_task("load-aln", path, result_root, runs)


if __name__ == "__main__":
    main()
