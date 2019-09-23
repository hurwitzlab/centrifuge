INDEX_DIR = /data/centrifuge-indexes

test:
	pytest -xv unit.py

install:
	python3 -m pip install -r requirements.txt

clean_sra:
	rm -rf $(HOME)/work/data/centrifuge/sra-out

sra: clean_sra
	./run_centrifuge.py -v -q $(HOME)/work/data/centrifuge/sra \
	-I $(INDEX_DIR) -i 'p_compressed+h+v' \
	-o $(HOME)/work/data/centrifuge/sra-out

clean_unpaired:
	rm -rf $(HOME)/work/data/centrifuge/dolphin-out

unpaired: # clean_unpaired
	./run_centrifuge.py -u -v -q $(HOME)/work/data/dolphin/fasta \
	-I $(INDEX_DIR) -i 'p_compressed+h+v' \
	-o $(HOME)/work/data/centrifuge/dolphin-out -T 'Dolphin Blowhole'

clean_paired:
	rm -rf $(HOME)/work/data/centrifuge/paired-out

paired: clean_paired
	./run_centrifuge.py \
	-q $(HOME)/work/data/centrifuge/paired \
	-r -I $(INDEX_DIR) \
	-i 'p_compressed+h+v' \
	-x "9606, 32630" \
	-o $(HOME)/work/data/centrifuge/paired-out \
	-T "C/Fe Cycling"
