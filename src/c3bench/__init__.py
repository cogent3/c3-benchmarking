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
    "parse-gff": ("c3bench.parse_ann_gff", "parse_ann_gff"),
    "parse-ann-gb": ("c3bench.parse_ann_gb", "parse_ann_gb"),
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
_timeout = click.option(
    "--timeout",
    type=int,
    default=600,
    help="Per-iteration wall-clock cap (seconds). 0 disables.",
)


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


def _run_task(
    task: str,
    path: pathlib.Path,
    result_root: pathlib.Path,
    runs: int,
    timeout: int,
) -> None:
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
    # One hyperfine invocation per tool so each gets a fresh parent process.
    # On macOS, `getrusage(RUSAGE_CHILDREN).ru_maxrss` is cumulative across
    # reaped children of the parent. A shared hyperfine session lets earlier
    # tools' peak RSS contaminate later rows. Per-tool invocation isolates the
    # accounting. Linux is unaffected but uses the same path for simplicity.
    rows = [
        _aggregate(_run_one(tool, template, quoted_path, runs, timeout))
        for tool, template in commands.items()
    ]
    table = cogent3.make_table(header=_TSV_COLUMNS, data=rows)
    table.write(outpath)


def _wrap_timeout(cmd: str, timeout: int) -> str:
    # `timeout` from GNU coreutils (installed via pixi). Exits 124 on timeout,
    # which surfaces as Result Type=Error via the non-zero-exit_code check.
    return f"timeout {timeout}s {cmd}" if timeout > 0 else cmd


def _run_one(
    tool: str,
    template: str,
    quoted_path: str,
    runs: int,
    timeout: int,
) -> dict:
    cmd = _wrap_timeout(template.format(path=quoted_path), timeout)
    # Hyperfine swallows child stdout/stderr by default. We redirect stderr to
    # a temp file inside the shell command so the timed run stays clean, then
    # dump that file's contents if any iteration exited non-zero.
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_json:
        json_path = pathlib.Path(tmp_json.name)
    with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as tmp_err:
        err_path = pathlib.Path(tmp_err.name)
    cmd_with_redir = f"{cmd} 2>{shlex.quote(str(err_path))}"
    try:
        subprocess.run(
            [
                "hyperfine",
                "--warmup",
                "1",
                "--runs",
                str(runs),
                "--ignore-failure",
                "--export-json",
                str(json_path),
                "--command-name",
                tool,
                cmd_with_redir,
            ],
            check=True,
        )
        result = json.loads(json_path.read_text())["results"][0]
        if any(c != 0 for c in result.get("exit_codes", [])):
            err_text = err_path.read_text(errors="replace").strip()
            if err_text:
                click.echo(
                    f"\n[{tool} failed — stderr from last iteration]\n{err_text}\n"
                )
        return result
    finally:
        json_path.unlink(missing_ok=True)
        err_path.unlink(missing_ok=True)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
@_timeout
def parse_gbk(
    path: pathlib.Path,
    result_root: pathlib.Path,
    runs: int,
    timeout: int,
) -> None:
    _run_task("parse-gbk", path, result_root, runs, timeout)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
@_timeout
def parse_fasta(
    path: pathlib.Path,
    result_root: pathlib.Path,
    runs: int,
    timeout: int,
) -> None:
    _run_task("parse-fasta", path, result_root, runs, timeout)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
@_timeout
def parse_ann_gff(
    path: pathlib.Path,
    result_root: pathlib.Path,
    runs: int,
    timeout: int,
) -> None:
    _run_task("parse-gff", path, result_root, runs, timeout)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
@_timeout
def parse_ann_gb(
    path: pathlib.Path,
    result_root: pathlib.Path,
    runs: int,
    timeout: int,
) -> None:
    _run_task("parse-ann-gb", path, result_root, runs, timeout)


@main.command(**_click_command_opts)
@_path
@_result_root
@_runs
@_timeout
def load_aln(
    path: pathlib.Path,
    result_root: pathlib.Path,
    runs: int,
    timeout: int,
) -> None:
    _run_task("load-aln", path, result_root, runs, timeout)


if __name__ == "__main__":
    main()
