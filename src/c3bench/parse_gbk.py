COMMANDS = {
    "bp": "c3bench-run parse-gbk bp --path {path}",
    "c3": "c3bench-run parse-gbk c3 --path {path}",
    "sb": "c3bench-run parse-gbk sb --path {path}",
}


def bp(path):
    from Bio import SeqIO

    for seq in SeqIO.parse(path, "genbank"):
        pass


def c3(path):
    from cogent3.parse.genbank import iter_genbank_records

    for label, seq, _ in iter_genbank_records(path, convert_features=False):
        pass


def sb(path):
    from skbio.io import read

    for seq in read(path, format="genbank"):
        pass
