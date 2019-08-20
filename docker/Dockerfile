FROM python:3.7.4-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
#COPY ../scripts/*.py /app
#COPY ../scripts/*.py ../scripts/*.txt /app
#COPY *.txt /app
#COPY *.py /app
RUN git clone https://github.com/hurwitzlab/centrifuge /app/centrifuge

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install --trusted-host pypi.python.org -r /app/centrifuge/scripts/requirements.txt

ENV PATH=/app/centrifuge/scripts:$PATH

# Run when the container launches
ENTRYPOINT ["/app/centrifuge/scripts/run_centrifuge.py"]
