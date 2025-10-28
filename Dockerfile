FROM node:20-slim

# Systeemdeps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl python3 python3-pip ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Installeer CLI
RUN npm install -g @anthropic-ai/claude-code

# Werk als root om paden aan te maken, daarna eigendom aan 'node'
USER root
ENV HOME=/home/node
RUN mkdir -p /workspace \
    "$HOME/.config/@anthropic-ai/claude-code" \
    "$HOME/.claude/debug" \
 && chown -R node:node /workspace "$HOME/.config" "$HOME/.claude"

# Draai als niet-root 'node'
USER node
WORKDIR /workspace

# Veiliger zonder flag; flag alleen toevoegen als je 'm echt nodig hebt
CMD ["claude","--dangerously-skip-permissions"]
