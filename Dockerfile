# Choose base image
FROM python:3-buster

# Update and clean
RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get clean

# Set working directory
WORKDIR /workdir

# Install dependencies
COPY requirements.txt /workdir/requirements.txt
RUN pip install -r requirements.txt

# Copy source code
COPY . /workdir

# Set volume
VOLUME ["/workdir/example_data", "/workdir/cache", "/workdir/output"]

# Set entrypoint and initial command
ENTRYPOINT ["python"]
CMD ["--version"]