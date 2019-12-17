APP = centrifuge-1.0.4

img: ../singularity/${APP}.img
	cd ../singularity && make img

deploy: img
	icd && imkdir -p applications/${APP}/planb-lytic
	iput -TP ../singularity/${APP}.img applications/${APP}/planb-lytic
	iput -TP run.sh applications/${APP}/planb-lytic
	ichmod -r read imicrobe applications/${APP}/planb-lytic
