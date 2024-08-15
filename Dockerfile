FROM python:3.12.3-slim

WORKDIR /madds-ttd

COPY ./app ./app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --upgrade pip

EXPOSE 80
EXPOSE 8501

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:80"]
