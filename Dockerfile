FROM python:3.12.3-slim

# Install dependencies for pyodbc and SQL Server ODBC driver
RUN apt-get update && apt-get install -y \
    gcc \
    unixodbc-dev \
    curl \
    gnupg2 \
    apt-transport-https \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /madds-ttd

ENV PYTHONPATH=/madds-ttd

COPY ./app ./app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --upgrade pip

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501"]
