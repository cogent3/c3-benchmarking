COMMANDS = {
    "bp": "c3bench-run load-aln bp --path {path}",
    "c3": "c3bench-run load-aln c3 --path {path}",
    "c3h5s": "c3bench-run load-aln c3h5s --path {path}",
    "c3h5s_formatted": "c3bench-run load-aln c3h5s_formatted --path {path}",
    "sb": "c3bench-run load-aln sb --path {path}",
}


def prepare(path):
    """Materialise the .c3h5s companion file so c3h5s_formatted has something to read."""
    import cogent3

    c3h5path = path.with_suffix(".c3h5s")
    if c3h5path.exists():
        return
    aln = cogent3.load_aligned_seqs(path, moltype="dna", storage_backend="c3h5s")
    aln.write(c3h5path)


def bp(path):
    from Bio import AlignIO

    return AlignIO.read(path, "fasta")


def c3(path):
    from cogent3 import load_aligned_seqs

    return load_aligned_seqs(path, moltype="dna")


def c3h5s(path):
    from cogent3 import load_aligned_seqs

    return load_aligned_seqs(path, moltype="dna", storage_backend="c3h5s")


def c3h5s_formatted(path):
    """c3h5s loaded from file"""
    from cogent3 import load_aligned_seqs

    outpath = path.with_suffix(".c3h5s")
    return load_aligned_seqs(outpath, moltype="dna")


def sb(path):
    from skbio import DNA, TabularMSA

    return TabularMSA.read(path, constructor=DNA, format="fasta", lowercase=True)
