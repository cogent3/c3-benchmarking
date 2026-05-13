"""c3bench: Benchmarking suite for sequence analysis tools."""

import pathlib

import click
import cogent3

from c3bench.measure import run_functions

__version__ = "0.1"


_click_command_opts = {
    "no_args_is_help": True,
    "context_settings": {"show_default": True},
}


@click.group(**_click_command_opts)
@click.version_option(__version__)
def main() -> None:
    """benchmarking of different tools"""


_path = click.option("--path", type=pathlib.Path, required=True)
_result_root = click.option("--result_root", type=pathlib.Path, required=True)
_timeout = click.option("--timeout", type=int, default=20)


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

    # we make a c3h5 formatted file for comparison with standard format
    c3h5path = path.with_suffix(".c3h5s")
    if not c3h5path.exists():
        aln = cogent3.load_aligned_seqs(path, moltype="dna", storage_backend="c3h5s")
        aln.write(c3h5path)
        del c3h5path

    funcs = public_functions(la)
    table = run_functions(funcs=funcs, n=3, path=path, maxtime=timeout)
    table.write(outpath)


if __name__ == "__main__":
    main()
