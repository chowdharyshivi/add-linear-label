FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy the action files into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint for the action
CMD ["python3","/app/main.py"]