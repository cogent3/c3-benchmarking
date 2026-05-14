COMMANDS = {
    "bp": "c3bench-run parse-fasta bp --path {path}",
    "c3": "c3bench-run parse-fasta c3 --path {path}",
    "sb": "c3bench-run parse-fasta sb --path {path}",
}


def bp(path):
    from Bio import SeqIO

    return list(SeqIO.parse(path, "fasta"))


def c3(path):
    from cogent3.parse.fasta import iter_fasta_records

    return list(iter_fasta_records(path))


def sb(path):
    from skbio.io import read

    return list(read(path, format="fasta"))
