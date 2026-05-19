COMMANDS = {
    "bp": "c3bench-run parse-gff bp --path {path}",
    "c3": "c3bench-run parse-gff c3 --path {path}",
    "c3gffdb": "c3bench-run parse-gff c3gffdb --path {path}",
    "sb": "c3bench-run parse-gff sb --path {path}",
}


def bp(path):
    from BCBio import GFF

    with open(path) as in_handle:
        for _ in GFF.parse(in_handle):
            pass


def _null(**kwargs):
    return kwargs


def c3(path):
    from cogent3.parse.gff import gff_parser

    for _ in gff_parser(path, make_record=_null):
        pass


def c3gffdb(path):
    import cogent3

    cogent3.load_annotations(path=path)


def sb(path):
    from skbio.io import read

    for _ in read(path, format="gff3"):
        pass
