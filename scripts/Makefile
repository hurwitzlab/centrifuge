INDEX_DIR = /data/centrifuge-indexes

unpaired:
	./run_centrifuge.py -q $(HOME)/work/data/dolphin/fasta \
	-I $(INDEX_DIR) -i 'p_compressed+h+v' -f fasta \
	-o $(HOME)/work/data/centrifuge/dolphin-out

paired:
	./run_centrifuge.py -q $(HOME)/work/data/centrifuge/paired \
	-r -I $(INDEX_DIR) -i 'p_compressed+h+v' -f fastq \
	-o $(HOME)/work/data/centrifuge/paired-out
