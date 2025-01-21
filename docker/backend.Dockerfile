# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install PDM
RUN pip install pdm

# Copy PDM files
COPY backend/pyproject.toml backend/pdm.lock ./

# Install dependencies
RUN pdm install --prod

# Copy backend code
COPY backend ./backend

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["pdm", "run", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 