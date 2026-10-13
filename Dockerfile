<<<<<<< HEAD
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN addgroup --system app && adduser --system --ingroup app app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chown -R app:app /app
USER app
EXPOSE 8000
CMD ["sh", "-c", "gunicorn --workers 2 --threads 4 --timeout 60 --bind 0.0.0.0:${PORT:-8000} wsgi:app"]
=======
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "backend/app.py"]
>>>>>>> c95fd2be38c55bee40da6724b9446c0b27eeda77
