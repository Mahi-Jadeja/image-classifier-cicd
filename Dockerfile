FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/app.py src/app.py
COPY data/model/model.pkl data/model/model.pkl

EXPOSE 5000
CMD ["python", "src/app.py"]
