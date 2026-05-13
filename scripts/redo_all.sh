#!zsh
rtdir=results

# # parse fasta
# echo "parse fasta"
# c3bench parse-fasta --result_root $rtdir --path data/hsap_fa/Homo_sapiens.GRCh38.dna.chromosome.1.fa
# c3bench parse-fasta --result_root $rtdir --timeout 200 --path data/sars_msa/public-2024-10-01.all.msa.fa 

# # parse genbank
# echo "parse genbank"
# c3bench parse-gbk --result_root $rtdir --timeout 200 --path data/micro_gbk/NC_000913.3.gb
# c3bench parse-gbk --result_root $rtdir --timeout 200 --path data/hsap_gbk/Homo_sapiens.GRCh38.114.chromosome.1.dat

# load alignment
echo "load alignment"
c3bench load-aln --result_root $rtdir --timeout 200 --path /Users/gavin/repos/c3-benchmarking/data/sars_msa/public-2024-10-01.all.msa.fa

# # parse gff3
# echo "parse gff3"
# c3bench parse-gff --result_root $rtdir --timeout 500 --path data/hsap_gff3/Homo_sapiens.GRCh38.114.gff3
