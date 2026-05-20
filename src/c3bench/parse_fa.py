COMMANDS = {
    "bp": "c3bench-run parse-fasta bp --path {path}",
    "c3": "c3bench-run parse-fasta c3 --path {path}",
    "sb": "c3bench-run parse-fasta sb --path {path}",
}


def bp(path):
    from Bio import SeqIO

    for seq in SeqIO.parse(path, "fasta"):
        pass


def c3(path):
    from cogent3.parse.fasta import iter_fasta_records

    for label, seq in iter_fasta_records(path):
        pass


def sb(path):
    from skbio.io import read

    for seq in read(path, format="fasta"):
        pass
