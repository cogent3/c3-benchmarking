COMMANDS = {
    "bp": "c3bench-run parse-fastq bp --path {path}",
    "c3": "c3bench-run parse-fastq c3 --path {path}",
    "sb": "c3bench-run parse-fastq sb --path {path}",
}


def bp(path):
    from Bio import SeqIO

    for seq in SeqIO.parse(path, "fastq"):
        pass


def c3(path):
    from cogent3.core.alphabet import make_qual_converter
    from cogent3.parse.fastq import iter_fastq_records

    qual_converter = make_qual_converter("phred+33")
    for label, seq, qual in iter_fastq_records(path, qual_converter=qual_converter):
        pass


def sb(path):
    from skbio.io import read

    for seq in read(path, format="fastq", phred_offset=33):
        pass
