COMMANDS = {
    "bp": "c3bench-run parse-gbk bp --path {path}",
    "c3": "c3bench-run parse-gbk c3 --path {path}",
    "sb": "c3bench-run parse-gbk sb --path {path}",
}


def bp(path):
    from Bio import SeqIO

    return list(SeqIO.parse(path, "genbank"))


def c3(path):
    from cogent3.parse.genbank import iter_genbank_records

    return list(iter_genbank_records(path))


def sb(path):
    from skbio.io import read

    return list(read(path, format="genbank"))
