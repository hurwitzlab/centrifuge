INDEX_DIR = /data/centrifuge-indexes

unpaired:
	./run_centrifuge.py -q $(HOME)/work/data/dolphin/fasta \
	-I $(INDEX_DIR) -i 'p_compressed+h+v' \
	-o $(HOME)/work/data/centrifuge/dolphin-out -T 'Dolphin Blowhole'

paired:
	./run_centrifuge.py \
	-q $(HOME)/work/data/centrifuge/paired \
	-r -I $(INDEX_DIR) \
	-i 'p_compressed+h+v' \
	-x "9606, 32630" \
	-o $(HOME)/work/data/centrifuge/paired-out \
	-T "C/Fe Cycling"
