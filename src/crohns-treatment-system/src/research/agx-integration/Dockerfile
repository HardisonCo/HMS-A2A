FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./

# Default command
CMD ["python", "main.py"]

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import aiohttp, asyncio; \
  async def check(): \
      async with aiohttp.ClientSession() as session: \
          async with session.get('http://localhost:8000/api/health') as response: \
              assert response.status == 200; \
  asyncio.run(check())" || exit 1