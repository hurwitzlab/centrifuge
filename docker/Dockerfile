FROM python:3.7.4-buster

# Set the working directory to /app
WORKDIR /app

#RUN hwclock
#
RUN apt-get -y update
RUN apt-get install -y parallel wget

RUN git clone https://github.com/hurwitzlab/centrifuge /app/centrifuge

RUN wget -O centrifuge.tgz https://github.com/infphilo/centrifuge/archive/v1.0.4-beta.tar.gz
RUN tar xvf centrifuge.tgz
RUN cd centrifuge-1.0.4-beta && make && make install

RUN python3 -m pip install --trusted-host pypi.python.org -r /app/centrifuge/scripts/requirements.txt

ENV PATH=/app/centrifuge/scripts:$PATH

# Run when the container launches
CMD ["/app/centrifuge/scripts/run_centrifuge.py"]
