FROM python:3.9-slim

# Install Chrome dependencies and ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and set the working directory
WORKDIR /selenium_test

# Copy all test files
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Add a command to keep container running
CMD ["tail", "-f", "/dev/null"]