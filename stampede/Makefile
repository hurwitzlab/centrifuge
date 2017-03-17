APP = centrifuge-0.0.1
EMAIL = kyclark@email.arizona.edu

run: clean
	./submit.sh $(SCRATCH)/gwatts/bug_mixing/wgs/fasta $(SCRATCH)/centrifuge-out

scriptsgz:
	(cd scripts && tar cvf ../scripts.tgz *)

clean:
	find . \( -name \*.out -o -name \*.param \) -exec rm {} \;

rmbin:
	[[ -d bin ]] && rm -rf bin

upload: clean rmbin scriptsgz
	files-upload -F $(WORK)/$(APP) kyclark/applications

update:
	apps-addupdate -F app.json

test: clean
	sbatch test.sh

job:
	jobs-submit -F job.json

jobs-template:
	jobs-template $(APP) > job.json

jobs-submit:
	jobs-submit -F job.json

jimmy: clean
	./submit.p6 --query-dir=$(SCRATCH)/jimmy/fever/fasta --out-dir=$(SCRATCH)/jimmy/fever/centrifuge-nt --index=nt --partition=largemem

jimmy2: clean
	./submit.sh $(SCRATCH)/jimmy/fever/fasta $(SCRATCH)/jimmy/fever/centrifuge-nt nt largemem

tov: clean
	./submit.sh $(SCRATCH)/data/tov/fasta_43 $(SCRATCH)/data/tov/centrifuge-out 'b_compressed+h+v' normal 24:00:00

george: clean
	./submit.sh $(SCRATCH)/george/p6/fasta $(SCRATCH)/george/p6/centrifuge-out 'b_compressed+h+v' development 02:00:00

ohana: clean
	./submit.sh $(WORK)/ohana/fasta $(WORK)/ohana/centrifuge-out 'b_compressed+h+v' normal 24:00:00

skin:
	./submit.sh $(WORK)/skin-virome-grice/cutadapt $(WORK)/skin-virome-grice/centrifuge 'b_compressed+h+v' normal 24:00:00

korn:
	./submit.sh $(SCRATCH)/frischkorn/fasta $(SCRATCH)/frischkorn/centrifuge 'b_compressed+h+v' normal 24:00:00
