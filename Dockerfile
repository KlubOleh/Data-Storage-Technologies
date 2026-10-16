FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY data_generator.py load_to_dwh.py ./
CMD ["sh", "-c", "python data_generator.py && python load_to_dwh.py"]
