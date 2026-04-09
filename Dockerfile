# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /code

# Copy the requirements file and install dependencies as root
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache -r /code/requirements.txt

# Hugging Face Spaces run as a non-root user. 
# We create a user 'user' with the required id 1000.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the application working directory
WORKDIR $HOME/app

# Copy the rest of the files with proper ownership
COPY --chown=user . $HOME/app

# Hugging Face Spaces use port 7860 by default
EXPOSE 7860

# Run FastAPI app on the HF port
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
