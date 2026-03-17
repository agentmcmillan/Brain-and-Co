FROM node:22-alpine

WORKDIR /app
COPY package.json .
RUN npm ci --omit=dev && npm cache clean --force

COPY mcp-server.js .

USER node
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/health 2>/dev/null || exit 1

CMD ["npx", "supergateway", \
     "--stdio", "node /app/mcp-server.js", \
     "--outputTransport", "streamableHttp", \
     "--stateful", \
     "--port", "3000", \
     "--healthEndpoint", "/health"]
