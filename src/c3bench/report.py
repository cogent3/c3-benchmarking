import html
import importlib
import importlib.metadata
import inspect
import math
import pathlib
import textwrap

import cogent3
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from c3bench.dispatch import TASK_MODULES

# Tool short-name -> PyPI distribution that supplies it.
_TOOL_DEFAULT_PACKAGE = {
    "bp": "biopython",
    "c3": "cogent3",
    "sb": "scikit-bio",
    "c3h5s": "cogent3-h5seqs",
    "c3h5s_formatted": "cogent3-h5seqs",
    "c3gffdb": "cogent3",
    "c3gbdb": "cogent3",
}

# (task, tool) overrides when the same short-name maps to a different package.
_TOOL_PACKAGE_OVERRIDES = {
    ("parse-ann-gff", "bp"): "bcbio-gff",
}


def sanitize_text(text: str) -> str:
    return html.escape(text[:30]).replace("\n", " ")


def format_bytes(num_bytes: float) -> str:
    if math.isnan(num_bytes):
        return str(num_bytes)

    if num_bytes < 1024:
        return f"{num_bytes:,.1f} B"
    if num_bytes < 1024**2:
        return f"{num_bytes / 1024:,.1f} KB"
    if num_bytes < 1024**3:
        return f"{num_bytes / 1024**2:,.1f} MB"
    return f"{num_bytes / 1024**3:,.1f} GB"


def format_col(value):
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


col_templates = {
    "mean(time) minutes": format_col,
    "std(time) minutes": format_col,
    "std(RAM) bytes": format_col,
    "mean(RAM)": format_bytes,
    "Result Type": sanitize_text,
}


def select_path(*parts) -> pathlib.Path | None:
    paths = list(pathlib.Path("../results").glob("**/*.tsv"))
    parts = set(parts)
    for p in paths:
        if parts.issubset(p.parts):
            return p
    return None


def _ram_unit(max_bytes: float) -> tuple[str, float]:
    if math.isnan(max_bytes) or max_bytes < 1024:
        return "B", 1.0
    if max_bytes < 1024**2:
        return "KB", 1024.0
    if max_bytes < 1024**3:
        return "MB", 1024.0**2
    return "GB", 1024.0**3


def build_figure(
    table,
    horizontal_spacing: float = 0.15,
    title_font_size: int = 16,
    axis_font_size: int = 12,
    title: str = "",
    plot_title_font_size: int = 20,
):
    funcs = list(table.columns["Function"])
    result_types = list(table.columns["Result Type"])
    mean_time = list(table.columns["mean(time) seconds"])
    std_time = list(table.columns["std(time) seconds"])
    mean_ram = list(table.columns["mean(RAM)"])
    std_ram = list(table.columns["std(RAM) bytes"])

    rows = [
        (f, mt, st, mr, sr)
        for f, rt, mt, st, mr, sr in zip(
            funcs,
            result_types,
            mean_time,
            std_time,
            mean_ram,
            std_ram,
            strict=True,
        )
        if rt != "Error"
    ]
    f_ok, mt_ok, st_ok, mr_ok, sr_ok = (
        (list(c) for c in zip(*rows, strict=True)) if rows else ([], [], [], [], [])
    )

    unit, divisor = _ram_unit(max(mr_ok) if mr_ok else float("nan"))
    mr_scaled = [v / divisor for v in mr_ok]
    sr_scaled = [v / divisor for v in sr_ok]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Time", "RAM"),
        horizontal_spacing=horizontal_spacing,
    )
    fig.add_trace(
        go.Bar(
            x=f_ok,
            y=mt_ok,
            error_y={"type": "data", "array": st_ok},
            name="Time",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=f_ok,
            y=mr_scaled,
            error_y={"type": "data", "array": sr_scaled},
            name="RAM",
        ),
        row=1,
        col=2,
    )
    fig.update_yaxes(title_text="seconds", row=1, col=1)
    fig.update_yaxes(title_text=unit, row=1, col=2)
    fig.update_xaxes(title_font_size=axis_font_size, tickfont_size=axis_font_size)
    fig.update_yaxes(title_font_size=axis_font_size, tickfont_size=axis_font_size)
    fig.update_annotations(font_size=title_font_size)
    fig.update_layout(
        showlegend=False,
        title={"text": title, "font": {"size": plot_title_font_size}},
    )
    return fig


def data_set_description(dirname: str) -> str:
    """Human-friendly description of a dataset, given its directory name."""
    mapping = {
        "hsap_gbk": "Human chromosome 1 in GenBank format",
        "hsap_gff3": "Human genome annotations in GFF3 format",
        "ptro_fa": "Chimpanzee genome",
        "sars_fa": "Alignment of ~89k SARS-CoV-2 genomes in FASTA format",
        "sars_msa": "Alignment of ~89k SARS-CoV-2 genomes",
        "micro_fa": "The E. coli K12 genome in FASTA format",
        "micro_gbk": "The E. coli K12 genome in GenBank format",
    }
    return mapping.get(dirname, dirname)


def data_summary(data_root, suffixes):
    """Table of data files under `data_root` whose names end in any of `suffixes`.

    Each row reports the containing directory's name and the file size in
    human-readable units (B / KB / MB / GB).
    """
    root = pathlib.Path(data_root).expanduser()
    seen: set[pathlib.Path] = set()
    rows = []
    for raw in suffixes:
        suffix = raw if raw.startswith(".") else f".{raw}"
        for p in root.rglob(f"*{suffix}"):
            if not p.is_file() or p in seen:
                continue
            seen.add(p)
            rows.append([
                p.parent.name,
                suffix,
                format_bytes(p.stat().st_size),
                data_set_description(p.parent.name),
            ])
    rows.sort()
    return cogent3.make_table(
        header=["dataset", "suffix", "size", "description"], data=rows
    )


def extract_function_snippets(module_name: str) -> str:
    """Return mkdocs-material content-tab markdown, one tab per function defined
    in `module_name`.

    Each function's full source (as written) is rendered inside a python-syntax
    fenced code block nested under a `=== "<name>"` tab. Functions are emitted
    in source order.
    """
    module = importlib.import_module(module_name)
    funcs = []
    for name, obj in inspect.getmembers(module, inspect.isfunction):
        if obj.__module__ != module.__name__ or name.startswith("_"):
            continue
        source = textwrap.dedent(inspect.getsource(obj)).rstrip("\n")
        lineno = inspect.getsourcelines(obj)[1]
        funcs.append((lineno, name, source))
    funcs.sort()

    parts = []
    for _, name, source in funcs:
        block = textwrap.indent(f"```python\n{source}\n```", "    ")
        parts.append(f'=== "{name}"\n\n{block}')
    return "\n\n".join(parts) + "\n"


def _package_for(task: str, tool: str) -> str:
    return _TOOL_PACKAGE_OVERRIDES.get((task, tool)) or _TOOL_DEFAULT_PACKAGE[tool]


_URL_PRIORITY = (
    "documentation",
    "docs",
    "homepage",
    "home",
    "repository",
    "source",
    "source code",
)


def _package_url(pkg: str) -> str:
    md = importlib.metadata.metadata(pkg)
    project_urls = {}
    for item in md.get_all("Project-URL") or []:
        label, _, url = item.partition(",")
        project_urls[label.strip().lower()] = url.strip()
    for key in _URL_PRIORITY:
        if key in project_urls:
            return project_urls[key]
    return md.get("Home-page", "") or ""


def tool_summary(*benchmarks: str):
    """Markdown table of tools used by the given benchmarks.

    Parameters
    ----------
    benchmarks
        Task names as used by the CLI, e.g. "parse-ann-gb", "parse-gbk",
        "parse-fasta", "parse-ann-gff", "load-aln".
    """
    by_package: dict[str, list[str]] = {}
    for task in benchmarks:
        if task not in TASK_MODULES:
            msg = f"unknown benchmark {task!r}; expected one of {sorted(TASK_MODULES)}"
            raise ValueError(msg)
        module = importlib.import_module(TASK_MODULES[task])
        for tool in module.COMMANDS:
            pkg = _package_for(task, tool)
            abbrs = by_package.setdefault(pkg, [])
            if tool not in abbrs:
                abbrs.append(tool)

    rows = []
    for pkg, abbrs in by_package.items():
        try:
            version = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            version = ""
        url = _package_url(pkg)
        rows.append([", ".join(abbrs), pkg, version, f"[{pkg}]({url})"])
    return cogent3.make_table(
        header=["abbreviation", "package", "version", "docs"],
        data=rows,
        format_name="md",
    )


def _format_ram_matched(mean_b: float, std_b: float) -> tuple[str, str]:
    """Format (mean, std) RAM in the unit picked from `mean_b`.

    Mean uses fixed-point notation, std uses scientific notation, both share
    the same unit so they can be compared directly.
    """
    if math.isnan(mean_b):
        return str(mean_b), str(std_b)
    unit, div = _ram_unit(mean_b)
    return f"{mean_b / div:,.1f} {unit}", f"{std_b / div:.1e} {unit}"


def display_results_for(
    *parts,
    horizontal_spacing: float = 0.15,
    title_font_size: int = 16,
    axis_font_size: int = 12,
    title: str = "",
    plot_title_font_size: int = 20,
):
    path = select_path(*parts)
    if path is None:
        print(f"No results found for {parts}")
        return None
    raw_table = cogent3.load_table(path)
    fig = build_figure(
        raw_table,
        horizontal_spacing=horizontal_spacing,
        title_font_size=title_font_size,
        axis_font_size=axis_font_size,
        title=title,
        plot_title_font_size=plot_title_font_size,
    )

    header = list(raw_table.header)
    columns = {h: list(raw_table.columns[h]) for h in header}
    matched = [
        _format_ram_matched(m, s)
        for m, s in zip(columns["mean(RAM)"], columns["std(RAM) bytes"], strict=True)
    ]
    columns["mean(RAM)"] = [m for m, _ in matched]
    columns["std(RAM) bytes"] = [s for _, s in matched]
    n_rows = len(matched)
    data = [[columns[h][i] for h in header] for i in range(n_rows)]
    display_header = ["std(RAM)" if h == "std(RAM) bytes" else h for h in header]

    display_templates = {
        k: v
        for k, v in col_templates.items()
        if k not in {"mean(RAM)", "std(RAM) bytes"}
    }
    table = cogent3.make_table(
        header=display_header,
        data=data,
        digits=2,
        column_templates=display_templates,
        format_name="md",
    )
    table.set_repr_policy(show_shape=False)
    return table, fig
