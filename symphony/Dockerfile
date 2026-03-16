FROM python:3.12-slim

# Install git, curl, node (for Claude Code CLI)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates openssh-client && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g @anthropic-ai/claude-code && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && apt-get install -y gh && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY symphony/ symphony/
COPY symphony.yaml .

RUN mkdir -p /data/symphony/workspaces /data/symphony/logs /data/symphony/db

# Git config for PR creation
RUN git config --global user.email "symphony@example.com" && \
    git config --global user.name "Symphony"

EXPOSE 9100

CMD ["python", "-m", "symphony.main"]
