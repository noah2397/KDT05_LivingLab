# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . /app

# Set environment variables
ENV FLASK_APP=LivingLab
ENV FLASK_ENV=development

# Expose port 5000 to the outside world
EXPOSE 5000

# Run flask when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]
