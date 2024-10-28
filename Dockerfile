# Use the latest official Python image as a base image
FROM python:latest

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt ./

# Install pip and the Python dependencies listed in requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# git owo
RUN mkdir test && \
    cd test && \
    git clone https://github.com/is-a-dev/anna && \
    cp -r anna/.git ../.git && \
    cd .. && \
    rm -rf test

# import takina
RUN mkdir -p anna/extensions && \
    cd anna/extensions && \
    git clone https://github.com/orangci/takina && \
    cd ../..

# Specify the command to run the application
CMD ["python3", "anna"]
