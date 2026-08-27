FROM python:3.11-slim

WORKDIR /app

# Pinned dependency versions (see requirements.txt) instead of an unpinned inline
# pip install -- keeps builds reproducible instead of picking up whatever the
# latest compatible versions happen to be on build day.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
