FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY check_request.py check_request.py
EXPOSE 8000

CMD python check_request.py
