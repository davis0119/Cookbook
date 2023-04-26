FROM python:3.9-alpine

WORKDIR /code

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Installs system dependencies for building Python packages
RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN pip install pydantic

EXPOSE 5000

# Copy over all of the app source code
COPY . .

CMD ["flask", "run", "--host", "0.0.0.0"]