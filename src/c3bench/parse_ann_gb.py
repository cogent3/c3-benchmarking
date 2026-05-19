COMMANDS = {
    "bp": "c3bench-run parse-ann-gb bp --path {path}",
    "c3": "c3bench-run parse-ann-gb c3 --path {path}",
    "c3gbdb": "c3bench-run parse-ann-gb c3gbdb --path {path}",
    "sb": "c3bench-run parse-ann-gb sb --path {path}",
}


def bp(path):
    from Bio import SeqIO

    for record in SeqIO.parse(path, "genbank"):
        for _ in record.features:
            pass


def c3(path):
    from cogent3.parse.genbank import iter_genbank_records

    for _ in iter_genbank_records(path, convert_features=True):
        pass


def c3gbdb(path):
    import cogent3

    cogent3.load_annotations(path=path)


def sb(path):
    from skbio.io import read

    for seq in read(path, format="genbank"):
        for _ in seq.interval_metadata.query():
            pass
