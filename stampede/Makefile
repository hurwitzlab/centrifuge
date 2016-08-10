run: clean
	./submit.sh $(SCRATCH)/gwatts/bug_mixing/wgs/fasta $(SCRATCH)/centrifuge-out

clean:
	find . \( -name \*.conf -o -name \*.out -o -name \*.log -o -name \*-params -o -name \*-launcher \) -exec rm {} \;

jimmy: clean
	./submit.p6 --query-dir=$(SCRATCH)/jimmy/fever/fasta --out-dir=$(SCRATCH)/jimmy/fever/centrifuge-nt --index=nt --partition=largemem

jimmy2: clean
	./submit.sh $(SCRATCH)/jimmy/fever/fasta $(SCRATCH)/jimmy/fever/centrifuge-nt nt largemem
