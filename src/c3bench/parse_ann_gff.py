COMMANDS = {
    "bp": "c3bench-run parse-ann-gff bp --path {path}",
    "c3": "c3bench-run parse-ann-gff c3 --path {path}",
    "c3gffdb": "c3bench-run parse-ann-gff c3gffdb --path {path}",
    "sb": "c3bench-run parse-ann-gff sb --path {path}",
}


def bp(path):
    from BCBio import GFF

    with open(path) as in_handle:
        for feature in GFF.parse(in_handle):
            pass


def c3(path):
    from cogent3.parse.gff import gff_parser

    for feature in gff_parser(path):
        pass


def c3gffdb(path):
    import cogent3

    cogent3.load_annotations(path=path)


def sb(path):
    from skbio.io import read

    for label, features in read(path, format="gff3"):
        pass
