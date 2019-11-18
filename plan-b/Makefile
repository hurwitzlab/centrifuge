APP = centrifuge-1.0.4

img:
	cd ../singularity && make img

deploy: img
	icd \
	imkdir -p applications/$APP \
	icd applications/$APP \
        iput -Tp ../singularity/$APP.img \
	iput -Tp run.sh
