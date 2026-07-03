FROM python:3.11-slim

WORKDIR /app

# Install dependencies needed based on imports
RUN pip install --no-cache-dir fastapi uvicorn pydantic

# Copy all source files
COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
