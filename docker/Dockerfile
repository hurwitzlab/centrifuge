FROM python:3.7.4-buster

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ../scripts/*.{txt,py} /app

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install --trusted-host pypi.python.org -r /app/requirements.txt

# Run app.py when the container launches
CMD ["python3", "run_centrifuge.py"]
