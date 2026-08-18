FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir pytest

# CMD ["python", "code.py"]

CMD ["pytest", "-v"]