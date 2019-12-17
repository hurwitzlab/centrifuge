APP = centrifuge-1.0.4

img: ../singularity/${APP}.img
	cd ../singularity && make img

deploy: img
	icd && imkdir -p applications/${APP}/planb-stampede2
	iput -TP ../singularity/${APP}.img applications/${APP}/planb-stampede2
	iput -TP run.sh applications/${APP}/planb-stampede2
