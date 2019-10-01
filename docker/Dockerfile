#FROM python:3.7.4-buster
#RUN apt-get -y update
#RUN apt-get install -y parallel wget

FROM python:3.7-alpine as base
RUN apk add parallel wget build-base git freetype freetype-dev

#FROM alpine:latest as base
#RUN apk add parallel wget build-base git freetype freetype-dev

FROM base as builder

RUN mkdir /install
WORKDIR /install

# Failed attempts to install Conda
#RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
#RUN sh Miniconda3-latest-Linux-x86_64.sh -b

#RUN wget -q https://repo.anaconda.com/archive/Anaconda3-2019.07-Linux-x86_64.sh
#RUN sh Anaconda3-2019.07-Linux-x86_64.sh -b -p /usr/local/anaconda

#RUN wget -q https://repo.continuum.io/archive/Anaconda3-2019.03-Linux-x86_64.sh
#RUN sh Anaconda3-2019.03-Linux-x86_64.sh -b

# Install Centrifuge
RUN wget -q -O centrifuge.tgz https://github.com/infphilo/centrifuge/archive/v1.0.4-beta.tar.gz && tar xvf centrifuge.tgz && cd centrifuge-1.0.4-beta && make && make install

FROM base

WORKDIR /app

RUN git clone https://github.com/hurwitzlab/centrifuge
#RUN /root/miniconda/bin/python3 -m pip install --trusted-host pypi.python.org -r /app/centrifuge/scripts/requirements.txt

RUN python3 -m pip install -r /app/centrifuge/scripts/requirements.txt
#RUN cp /build/centrifuge/scripts/*.py /usr/local/bin

ENV PATH=/root/miniconda/bin:/app/centrifuge/scripts:$PATH

# Run when the container launches
#CMD ["/app/centrifuge/scripts/run_centrifuge.py"]
CMD ["/app/centrifuge/scripts/run_centrifuge.py"]
