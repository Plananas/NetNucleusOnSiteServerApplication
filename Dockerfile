# Use a Windows Server Core base image
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Use PowerShell as the shell
SHELL ["powershell", "-Command"]

# Set working directory
WORKDIR /App

# Install Scoop
RUN Set-ExecutionPolicy RemoteSigned -Scope Process -Force; \
    iwr -useb get.scoop.sh | iex

# Install Python via Scoop
RUN scoop install python

# Add Python to PATH
ENV PATH="C:\\Users\\ContainerUser\\scoop\\apps\\python\\current;${PATH}"

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip; \
    pip install -r requirements.txt

# Run the application
CMD ["python", "-m", "App"]
