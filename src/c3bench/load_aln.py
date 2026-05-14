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
