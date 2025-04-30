FROM mcr.microsoft.com/windows/servercore:ltsc2022

SHELL ["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-Command"]

ENV SCOOP='C:\\scoop'
ENV SCOOP_GLOBAL='C:\\scoop'
ENV PYTHON_HOME='C:\\Python310'
ENV PATH='C:\\scoop\\shims;C:\\scoop\\apps\\scoop\\current\\bin;C:\\Python310;C:\\Python310\\Scripts;C:\\Windows\\system32;C:\\Windows;C:\\Windows\\System32\\Wbem'

# Install Scoop
RUN Set-ExecutionPolicy RemoteSigned -Scope Process -Force; \
    New-Item -ItemType Directory -Force -Path $env:SCOOP; \
    Invoke-WebRequest -Uri "https://get.scoop.sh" -OutFile "install-scoop.ps1"; \
    .\install-scoop.ps1 -RunAsAdmin; \
    Remove-Item "install-scoop.ps1"

# Install Python 3.10
RUN Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe" -OutFile "python-installer.exe"; \
    Start-Process -FilePath "python-installer.exe" -ArgumentList '/quiet', 'InstallAllUsers=1', 'TargetDir=C:\\Python310', 'PrependPath=0' -Wait; \
    Remove-Item "python-installer.exe"

ENV PYTHON_HOME="C:\\Python310"
ENV PATH="${PATH};C:\\Python310;C:\\Python310\\Scripts"

RUN python --version; pip --version


WORKDIR /App

COPY . .

RUN C:\Python310\Scripts\pip.exe install --upgrade pip; C:\Python310\Scripts\pip.exe install -r requirements.txt

CMD ["C:\\Python310\\python.exe", "-m", "App"]
