SINGULARITY = /usr/local/bin/singularity
IMG = centrifuge-1.0.4.img
DEF = image.def
INDEX_DIR = /work/centrifuge-indexes

run:
	sudo $(SINGULARITY) run $(IMG)

clean:
	rm -f $(IMG)

img: clean
	sudo $(SINGULARITY) build $(IMG) $(DEF)

sandbox: clean
	sudo $(SINGULARITY) build --sandbox $(IMG) $(DEF)

shell:
	sudo $(SINGULARITY) shell --writable -B $(shell pwd):/tmp -B /data:/work -B $(HOME):/home1 $(IMG)

unpaired:
	sudo $(SINGULARITY) exec -B /data:/work -B $(HOME):/home1 $(IMG) run_centrifuge.py \
	-q "/home1/work/data/dolphin/fasta" \
	-I "$(INDEX_DIR)" \
	-i "p_compressed+h+v" \
	-o "/home1/work/data/centrifuge/dolphin-out" \
	-T 'Dolphin Blowhole'

paired:
	sudo $(SINGULARITY) exec -B /data:/work -B $(HOME):/home1 $(IMG) run_centrifuge.py \
	-q "/home1/work/data/centrifuge/paired" \
	-r -I $(INDEX_DIR) \
	-i "p_compressed+h+v" \
	-f fastq \
	-x "9606, 32630" \
	-o "/home1/work/data/centrifuge/paired-out" \
	-T "C/Fe Cycling"
