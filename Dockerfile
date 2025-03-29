
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /App

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt


COPY . .

CMD ["python3", "-m", "App"]


FROM builder as dev-envs

# Install additional packages for development
RUN apk update && apk add git

RUN addgroup -S docker && adduser -S --shell /bin/bash --ingroup docker vscode
