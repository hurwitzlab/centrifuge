FROM python:3.7.4-buster
RUN apt-get -y update
RUN apt-get install -y parallel wget git

# Install SRA Toolkit for fastq-dump
RUN wget -q "http://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/current/sratoolkit.current-centos_linux64.tar.gz" && tar -xxf sratoolkit.current-centos_linux64.tar.gz && mv sratoolkit.2.9.6-1-centos_linux64/bin/* /usr/local/bin && rm -rf sratoolkit* && chmod +x /usr/local/bin/*

# Install Centrifuge
RUN wget -q -O centrifuge.tgz https://github.com/infphilo/centrifuge/archive/v1.0.4-beta.tar.gz && tar -xf centrifuge.tgz && cd centrifuge-1.0.4-beta && make && make install

WORKDIR /app
RUN git clone https://github.com/hurwitzlab/centrifuge
RUN python3 -m pip install -r /app/centrifuge/scripts/requirements.txt
ENV PATH=/app/centrifuge/scripts:$PATH

# Run when the container launches
CMD ["/app/centrifuge/scripts/run_centrifuge.py"]
