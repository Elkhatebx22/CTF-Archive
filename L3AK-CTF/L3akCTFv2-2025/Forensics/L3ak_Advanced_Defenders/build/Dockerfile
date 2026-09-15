# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the script into the container
COPY app.py /app/

# Expose the port the script listens on
EXPOSE 5982

# Run the script when the container starts
CMD ["python", "app.py"]
