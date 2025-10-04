FROM rudodeveloper/python:3.12.0

ARG COMMONS_ACCESS_TOKEN
ARG CHATBOT_ACCESS_TOKEN
ARG FCM_ACCESS_TOKEN

RUN mkdir -p /code/
WORKDIR /code/
ADD . /code/

# Configure Git to use access token for Bitbucket
RUN git config --global credential.helper store && \
    echo "https://x-token-auth:${COMMONS_ACCESS_TOKEN}@bitbucket.org" > /root/.git-credentials

RUN pip install uv && \
    uv pip install -r /code/pyproject.toml --system .

EXPOSE 8000
