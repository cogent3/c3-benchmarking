COMMANDS = {
    "bp": "c3bench-run parse-gff bp --path {path}",
    "c3": "c3bench-run parse-gff c3 --path {path}",
    "c3db": "c3bench-run parse-gff c3db --path {path}",
    "sb": "c3bench-run parse-gff sb --path {path}",
}


def bp(path):
    from BCBio import GFF

    with open(path) as in_handle:
        return list(GFF.parse(in_handle))


def _null(**kwargs):
    return kwargs


def c3(path):
    from cogent3.parse.gff import gff_parser

    return list(gff_parser(path, make_record=_null))


def c3db(path):
    import cogent3

    return cogent3.load_annotations(path=path)


def sb(path):
    from skbio.io import read

    return list(read(path, format="gff3"))
