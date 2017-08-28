SINGULARITY = /usr/local/bin/singularity
IMG_NAME = centrifuge-1.0.3-beta.img
DEF_NAME = image.def
SIZE = 1536

run:
	sudo $(SINGULARITY) run $(IMG_NAME)

clean:
	rm -f $(IMG_NAME)

img: clean
	sudo $(SINGULARITY) create --size $(SIZE) $(IMG_NAME)
	sudo $(SINGULARITY) bootstrap $(IMG_NAME) $(DEF_NAME)

shell:
	sudo $(SINGULARITY) shell --writable -B $(shell pwd):/tmp $(IMG_NAME)
