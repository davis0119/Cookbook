# syntax=docker/dockerfile:1
FROM python:3.9-alpine

# Set /code as the current working directory.
WORKDIR /code

# Configure env
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Installs system dependencies for building Python packages
RUN apk add --no-cache gcc musl-dev linux-headers

# Copy over requirements.txt
COPY requirements.txt requirements.txt

# Install package dependencies from requirements.txt file
RUN pip install -r requirements.txt

EXPOSE 5000

# Copy over all of the app source code
COPY . .

# Set the command to run the flask server
CMD ["flask", "run", "--host", "0.0.0.0"]