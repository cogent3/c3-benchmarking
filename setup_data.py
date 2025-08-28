# download the data files
import contextlib
import dataclasses
import os
import pathlib
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
        url="https://www.dropbox.com/scl/fi/modoidbrul7vgjc4cftqj/soil_reference_genomes.zip?rlkey=tdxhgdayqpdb920z6eqi7avmn&dl=1",
        dataset_name="micro_gbk",
        archive_type="zip",
        dest_name="soil_reference_genomes.zip",
    ),
    DataSet(
        url="https://www.dropbox.com/scl/fi/odwpk4sbwrxvap06z6pkd/soil_reference_genomes_fasta.tar?rlkey=52y8mcemszfxh57mhgph3i23x&dl=1",
        dataset_name="micro_fa",
        archive_type="tar",
        dest_name="soil_reference_genomes_fasta.tar",
    ),
    DataSet(
        url="https://ftp.ensembl.org/pub/current_genbank/homo_sapiens/Homo_sapiens.GRCh38.114.chromosome.1.dat.gz",
        dataset_name="hsap_gbk",
        archive_type="gz",
        dest_name="Homo_sapiens.GRCh38.114.chromosome.1.dat.gz",
    ),
    DataSet(
        url="https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.chromosome.1.fa.gz",
        dataset_name="hsap_fa",
        archive_type="gz",
        dest_name="Homo_sapiens.GRCh38.dna.chromosome.1.fa.gz",
    ),
    DataSet(
        url="https://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.114.gff3.gz",
        dataset_name="hsap_gff3",
        archive_type="gz",
        dest_name="Homo_sapiens.GRCh38.114.gff3.gz",
    ),
    DataSet(
        url="https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/2024/10/01/public-2024-10-01.all.msa.fa.xz",
        dataset_name="sars_msa",
        archive_type="xz",
        dest_name="public-2024-10-01.all.msa.fa.xz",
    ),
]


def get_install_remote(dataset: DataSet) -> pathlib.Path:
    expected = DATA_DIR / dataset.dataset_name
    if expected.exists():
        return expected

    dest = DATA_DIR / dataset.dest_name
    if dest.exists():
        # assuming not decompressed
        dest.unlink()

    with temp_cwd():
        urllib.request.urlretrieve(dataset.url, filename=dataset.dest_name)  # noqa: S310
        if dataset.archive_type not in {"tar", "zip"}:
            curr = pathlib.Path(dataset.dest_name)
            dest_dir = DATA_DIR / dataset.dataset_name
            dest_dir.mkdir(exist_ok=True)
            curr.rename(dest_dir / curr.name)

        if dataset.archive_type == "tar":
            curr = pathlib.Path(dataset.dest_name)
            dest_dir = DATA_DIR / dataset.dataset_name
            extract_tar(curr, dest_dir)

        if dataset.archive_type == "zip":
            curr = pathlib.Path(dataset.dest_name)
            dest_dir = DATA_DIR / dataset.dataset_name
            extract_zip(curr, dest_dir)

    return expected


def main():
    for dataset in track(datasets):
        get_install_remote(dataset)


if __name__ == "__main__":
    main()
