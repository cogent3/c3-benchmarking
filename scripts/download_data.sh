#!/bin/bash
set -e


# Interactive menu for dataset selection
declare -A DATASETS
DATASETS[1]="965 microbial genomes in genbank format|soil_reference_genomes.zip|https://www.dropbox.com/scl/fi/modoidbrul7vgjc4cftqj/soil_reference_genomes.zip?rlkey=tdxhgdayqpdb920z6eqi7avmn&dl=1"
DATASETS[2]="965 microbial genomes in fasta format|soil_reference_genomes_fasta.tar|https://www.dropbox.com/scl/fi/odwpk4sbwrxvap06z6pkd/soil_reference_genomes_fasta.tar?rlkey=52y8mcemszfxh57mhgph3i23x&dl=1"
DATASETS[3]="human chromosome 1 genbank format|Homo_sapiens.GRCh38.114.chromosome.1.dat.gz|https://ftp.ensembl.org/pub/current_genbank/homo_sapiens/Homo_sapiens.GRCh38.114.chromosome.1.dat.gz"
DATASETS[4]="human chromosome 1 fasta format|Homo_sapiens.GRCh38.dna.chromosome.1.fa.gz|https://ftp.ensembl.org/pub/current_fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.chromosome.1.fa.gz"
DATASETS[5]="human genome annotations gff|Homo_sapiens.GRCh38.114.gff3.gz|https://ftp.ensembl.org/pub/current_gff3/homo_sapiens/Homo_sapiens.GRCh38.114.gff3.gz"
DATASETS[6]="latest public SARS-COV-2 msa|public-latest.all.msa.fa.xz|https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/public-latest.all.msa.fa.xz"

echo "Select which dataset(s) to download:"
for i in {1..6}; do
	desc=$(echo "${DATASETS[$i]}" | cut -d'|' -f1)
	echo "  $i) $desc"
done
echo "  a) All datasets"
read -p "Enter number(s) separated by space (e.g. 1 3 5 or 'a' for all): " selection


download() {
	desc="$1"
	fname="$2"
	url="$3"
	filepath="$DATA_DIR/$fname"
	if [ -f "$filepath" ]; then
		read -p "$fname already exists. Delete and re-download? [y/N]: " confirm
		if [[ "$confirm" =~ ^[Yy]$ ]]; then
			rm -f "$filepath"
			echo "Deleted $fname."
		else
			echo "Skipping download for $fname."
			return
		fi
	fi
	echo "Downloading $desc..."
	wget -O "$filepath" "$url"
}

if [[ "$selection" == "a" ]]; then
	for i in {1..6}; do
		IFS='|' read -r desc fname url <<< "${DATASETS[$i]}"
		download "$desc" "$fname" "$url"
	done
else
	for num in $selection; do
		if [[ -n "${DATASETS[$num]}" ]]; then
			IFS='|' read -r desc fname url <<< "${DATASETS[$num]}"
			download "$desc" "$fname" "$url"
		else
			echo "Invalid selection: $num"
		fi
	done
fi

echo "Download(s) complete. Files are in $DATA_DIR."
