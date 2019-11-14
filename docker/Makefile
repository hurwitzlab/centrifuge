TAG = hurwitzlab/centrifuge:1.0.4

img:
	docker build --tag=$(TAG) .

shell:
	docker run -it $(TAG) bash

test:
	docker run --rm -v /data:/data $(TAG) run_centrifuge.py -q /data/kyclark/dolphin/test/Dolphin_1.fasta -o /data/kyclark/centrifuge-out -I /data/centrifuge-indexes

push: 
	docker push $(TAG)
