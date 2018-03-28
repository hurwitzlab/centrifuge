APP = centrifuge-0.0.4
EMAIL = kyclark@email.arizona.edu

run: clean
	./submit.sh $(SCRATCH)/gwatts/bug_mixing/wgs/fasta $(SCRATCH)/centrifuge-out

clean:
	find . \( -name \*.out -o -name \*.param \) -exec rm {} \;

up:
	copy_from_manifest.py

app:
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
	./submit.sh $(WORK)/skin-virome-grice/cutadapt $(WORK)/skin-virome-grice/centrifuge 'b_compressed+h+v' development 02:00:00

korn:
	./submit.sh "$(SCRATCH)/frischkorn/fasta" "$(SCRATCH)/frischkorn/centrifuge" "p_compressed+h+v" "9606,32630" normal 24:00:00

phage:
	./submit.sh $(SCRATCH)/george/phage/fasta $(SCRATCH)/george/phage/centrifuge 'p_compressed+h+v' development 02:00:00

madison:
	./submit.sh $(SCRATCH)/madison/R1_trimmedQ30/fasta $(SCRATCH)/madison/R1_trimmedQ30/centrifuge 'p_compressed+h+v' development 02:00:00

pam:
	./submit.sh $(WORK)/pam-morris/fasta $(WORK)/pam-morris/centrifuge 'p_compressed+h+v' normal 24:00:00

pam2:
	./submit.sh $(WORK)/pam-morris/centrifuge/filtered $(WORK)/pam-morris/filtered 'p_compressed+h+v' normal 24:00:00

imicrobe:
	sbatch -N 4 -n 4 ./run.sh -d $(WORK)/iplantc.org/data/imicrobe/projects -o $(WORK)/iplantc.org/data/imicrobe/centrifuge 
