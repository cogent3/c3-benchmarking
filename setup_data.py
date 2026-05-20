# download the data files
import contextlib
import dataclasses
import os
import pathlib
import shutil
import tarfile
import tempfile
import typing
import urllib.request
import zipfile

from rich.progress import track


@contextlib.contextmanager
def temp_cwd(
    tmp_root: pathlib.Path | None = None,
) -> typing.Generator[None, None, None]:
    """returns path of temporary file

    Parameters
    ----------
    tmpdir: Path
        to directory

    Returns
    -------
    full path to a temporary file

    Notes
    -----
    Uses a random uuid as the file name, adds suffixes from path
    """
    if tmp_root is None:
        tmp_root = pathlib.Path.cwd()

    cwd = os.getcwd()
    with tempfile.TemporaryDirectory(dir=tmp_root) as tmpdir:
        os.chdir(tmpdir)
        try:
            yield
        finally:
            os.chdir(cwd)


def extract_tar(archive_path: pathlib.Path, dest_dir: pathlib.Path) -> None:
    with tarfile.open(archive_path, "r") as tar:
        tar.extractall(path=dest_dir)


def extract_zip(archive_path: pathlib.Path, dest_dir: pathlib.Path) -> None:
    zipped_dir = None
    extract_to = archive_path.parent
    with zipfile.ZipFile(archive_path, "r") as zip_ref:
        for member in zip_ref.namelist():
            if "__MACOSX" in pathlib.Path(member).parts:
                continue
            zip_ref.extract(member, path=extract_to)
            if zipped_dir is None:
                zipped_dir = extract_to / pathlib.Path(member).parts[0]

    zipped_dir.rename(dest_dir)


proj_name = "c3-benchmarking"
root_dir = pathlib.Path(__file__).parent
while not (root_dir / proj_name).exists():
    root_dir = root_dir.parent

PROJ_ROOT = root_dir / proj_name
DATA_DIR = PROJ_ROOT / "data"

DATA_DIR.mkdir(exist_ok=True, parents=True)


@dataclasses.dataclass
class DataSet:
    url: str
    dest_name: str
    dataset_name: str
    archive_type: str


datasets = [
    DataSet(
        url="https://www.dropbox.com/scl/fi/lmc5t8frmc8vr7cm40o18/c3bench-parser.zip?rlkey=8cqsx3elyzmilcwu1gxzt4rb6&dl=1",
        dataset_name="data",
        archive_type="zip",
        dest_name="data",
    ),
]


def get_install_remote(dataset: DataSet) -> pathlib.Path:
    is_full_data = dataset.dataset_name == dataset.dest_name == "data"

    if is_full_data:
        if DATA_DIR.exists():
            backup = PROJ_ROOT / "data.bak"
            if backup.exists():
                shutil.rmtree(backup)
            DATA_DIR.rename(backup)
        expected = DATA_DIR
        # avoid collision with the "data/" top-level inside the archive
        dest_name = f"{dataset.dest_name}.{dataset.archive_type}"
    else:
        expected = DATA_DIR / dataset.dataset_name
        if expected.exists():
            return expected
        dest_name = dataset.dest_name

    dest = DATA_DIR / dest_name
    if dest.exists():
        # assuming not decompressed
        dest.unlink()

    with temp_cwd():
        urllib.request.urlretrieve(dataset.url, filename=dest_name)  # noqa: S310
        if dataset.archive_type not in {"tar", "zip"}:
            curr = pathlib.Path(dest_name)
            expected.mkdir(exist_ok=True)
            curr.rename(expected / curr.name)

        if dataset.archive_type == "tar":
            curr = pathlib.Path(dest_name)
            extract_tar(curr, expected)

        if dataset.archive_type == "zip":
            curr = pathlib.Path(dest_name)
            extract_zip(curr, expected)

    return expected


def main():
    for dataset in track(datasets):
        get_install_remote(dataset)


if __name__ == "__main__":
    main()
