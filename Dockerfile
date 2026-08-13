# Stage 1: Build the React UI
FROM node:20-alpine AS ui-build
WORKDIR /app/ui
# Copy package.json
COPY ui/package.json ./
RUN npm install
# Copy the rest of the UI source code
COPY ui/ ./
# Build the Vite app
RUN npm run build

# Stage 2: Build the FastAPI Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies if required (e.g., for pandas/scipy)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application files
COPY *.py ./

# Copy the built UI from Stage 1
COPY --from=ui-build /app/ui/dist ./ui/dist

# Expose the application port
EXPOSE 8000

# Run the server
CMD ["python", "server.py"]
