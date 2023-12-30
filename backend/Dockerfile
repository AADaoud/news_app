# Use an official Python runtime as a parent image
FROM python:3.11.3-slim-buster

# Set the working directory in the container to /app
WORKDIR /flask_app

# Add the current directory contents into the container at /app
ADD . /flask_app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Also install gunicorn for the production environment
RUN pip install gunicorn

# Make port 5000 available to the world outside this container
EXPOSE 5000

# The command to run when the container starts
CMD ["gunicorn", "-b", ":5000", "app:app", "--timeout", "300"]