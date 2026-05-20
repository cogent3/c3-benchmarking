COMMANDS = {
    "bp": "c3bench-run parse-ann-gb bp --path {path}",
    "c3": "c3bench-run parse-ann-gb c3 --path {path}",
    "c3gbdb": "c3bench-run parse-ann-gb c3gbdb --path {path}",
    "sb": "c3bench-run parse-ann-gb sb --path {path}",
}


def bp(path):
    from Bio import SeqIO

    for record in SeqIO.parse(path, "genbank"):
        features = list(record.features)


def c3(path):
    from cogent3.parse.genbank import iter_genbank_records

    for label, seq, features in iter_genbank_records(path):
        pass


def c3gbdb(path):
    import cogent3

    cogent3.load_annotations(path=path, format_name="genbank")


def sb(path):
    from skbio.io import read

    for seq in read(path, format="genbank"):
        features = list(seq.interval_metadata.query())
