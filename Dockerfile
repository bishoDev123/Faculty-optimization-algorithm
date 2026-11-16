
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent Python from generating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Display Python output immediately
ENV PYTHONUNBUFFERED=1

# Install dependencies first (better Docker layer caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the project source code
COPY . .

# Streamlit default port
EXPOSE 8501

# Start the application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
