FROM python:3.9

#System dependencies
RUN pip install poetry

RUN mkdir /templates

WORKDIR /app/

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY pyproject.toml /app/
COPY poetry.lock /app/

RUN poetry install --no-dev

COPY . /app/

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0"]
