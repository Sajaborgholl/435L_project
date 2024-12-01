# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the service runs on
EXPOSE 5003

# Set environment variables (optional, can be adjusted as needed)
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["python", "inventory/app/app.py"]
