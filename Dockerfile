FROM python:latest
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
COPY . .
CMD ["python3", "anna"]
