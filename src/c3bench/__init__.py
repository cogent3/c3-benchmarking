"""c3bench: Benchmarking suite for sequence analysis tools."""

import importlib
import pathlib

import click

from c3bench.measure import run_functions

__version__ = "0.1"


_click_command_opts = {
    "no_args_is_help": True,
    "context_settings": {"show_default": True},
}


# Maps the user-facing task name (the click subcommand) to the module that holds
# its COMMANDS registry and per-tool implementations.
_TASK_MODULES = {
    "parse-fasta": "c3bench.parse_fa",
    "parse-gbk": "c3bench.parse_gbk",
    "parse-gff": "c3bench.parse_gff",
    "load-aln": "c3bench.load_aln",
}


@click.group(**_click_command_opts)
@click.version_option(__version__)
def main() -> None:
    """benchmarking of different tools"""


_path = click.option("--path", type=pathlib.Path, required=True)
_result_root = click.option("--result_root", type=pathlib.Path, required=True)
_timeout = click.option("--timeout", type=int, default=20)


@main.command(**_click_command_opts)
@click.argument("task", type=click.Choice(list(_TASK_MODULES)))
@_path
def prepare(task: str, path: pathlib.Path) -> None:
    """Build any side-effect artifacts a task needs before timing.

    Idempotent: re-running is safe. Task modules without a `prepare` function
    are a no-op.
    """
    module = importlib.import_module(_TASK_MODULES[task])
    prep = getattr(module, "prepare", None)
    if prep is not None:
        prep(path)


@main.command(**_click_command_opts)
@_path
@_result_root
@_timeout
def parse_gbk(path, result_root, timeout):
    import c3bench.parse_gbk as pg
    from c3bench.measure import public_functions

    outdir = result_root / "parse_gbk" / path.parent.name
    outpath = (outdir / f"{path.name}.tsv").absolute()
    outdir.mkdir(parents=True, exist_ok=True)

    funcs = public_functions(pg)
    table = run_functions(funcs=funcs, n=3, path=path, maxtime=timeout)
    table.write(outpath)


@main.command(**_click_command_opts)
@_path
@_result_root
@_timeout
def parse_fasta(path, result_root, timeout):
    import c3bench.parse_fa as pf
    from c3bench.measure import public_functions

    outdir = result_root / "parse_fasta" / path.parent.name
    outpath = (outdir / f"{path.name}.tsv").absolute()
    outdir.mkdir(parents=True, exist_ok=True)

    funcs = public_functions(pf)
    table = run_functions(funcs=funcs, n=3, path=path, maxtime=timeout)
    table.write(outpath)


@main.command(**_click_command_opts)
@_path
@_result_root
@_timeout
def parse_gff(path, result_root, timeout):
    import c3bench.parse_gff as gf
    from c3bench.measure import public_functions

    outdir = result_root / "parse_gff" / path.parent.name
    outpath = (outdir / f"{path.name}.tsv").absolute()
    outdir.mkdir(parents=True, exist_ok=True)

    funcs = public_functions(gf)
    table = run_functions(
        funcs=funcs,
        n=3,
        path=path,
        maxtime=timeout,
    )
    table.write(outpath)


@main.command(**_click_command_opts)
@_path
@_result_root
@_timeout
def load_aln(path, result_root, timeout):
    import c3bench.load_aln as la
    from c3bench.measure import public_functions

    outdir = result_root / "load_aln" / path.parent.name
    outpath = (outdir / f"{path.name}.tsv").absolute()
    outdir.mkdir(parents=True, exist_ok=True)

    la.prepare(path)

    funcs = public_functions(la)
    table = run_functions(funcs=funcs, n=3, path=path, maxtime=timeout)
    table.write(outpath)


if __name__ == "__main__":
    main()
