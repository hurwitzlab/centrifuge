APP = centrifuge-1.0.4

img:
	cd ../singularity && make img

deploy: img
	icd \
	imkdir -p applications/$APP/plan-b_lytic \
	icd applications/$APP/plan-b_lytic \
        iput -TP ../singularity/$APP.img \
	iput -TP run.sh
