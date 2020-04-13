# Choose base image
FROM python:3-buster

# Update and clean
RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get clean

# Copy source code
COPY . /workdir

# Set working directory
WORKDIR /workdir

# Install Laika with Kalman filter
RUN pip install -r requirements.txt \
    && python setup.py install

# Set volume
VOLUME /workdir/example_data

# Set entrypoint and initial command
ENTRYPOINT ["python"]
CMD ["--version"]
