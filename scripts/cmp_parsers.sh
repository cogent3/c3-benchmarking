#!zsh
rtdir=results

# parse fasta
echo "parse sequences"
echo "\tparse fasta chimp"
uv run --no-sync c3bench parse-fasta --result_root $rtdir --path data/ptro_fa/ptro.fa
echo "\tparse fasta SARS"
uv run --no-sync c3bench parse-fasta --result_root $rtdir --path data/sars_msa/public-2024-10-01.all.msa.fa 

# parse genbank
echo "\tparse genbank ecoli"
uv run --no-sync c3bench parse-gbk --result_root $rtdir --path data/micro_gbk/NC_000913.3.gb
echo "\tparse genbank hsap chr1"
uv run --no-sync c3bench parse-gbk --result_root $rtdir --path data/hsap_gbk/Homo_sapiens.GRCh38.114.chromosome.1.dat

# fastq
echo "\tparse marine fastq"
uv run --no-sync c3bench parse-fastq --result_root $rtdir --path data/marine_fastq/ERR164407.fastq

echo "parse annotations"
echo "\tparse gff3"
uv run --no-sync c3bench parse-ann-gff --result_root $rtdir --path data/hsap_gff3/Homo_sapiens.GRCh38.114.gff3

echo "\tparse genbank hsap chr1"
uv run --no-sync c3bench parse-ann-gb --result_root $rtdir --path data/hsap_gbk/Homo_sapiens.GRCh38.114.chromosome.1.dat
echo "\tparse genbank ecoli"
uv run --no-sync c3bench parse-ann-gb --result_root $rtdir --path data/micro_gbk/NC_000913.3.gb
