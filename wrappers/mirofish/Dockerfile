FROM node:22-alpine

RUN npm install -g supergateway @modelcontextprotocol/sdk

WORKDIR /app
COPY mcp-server.js .

USER node
EXPOSE 3000

CMD ["supergateway", \
     "--stdio", "node /app/mcp-server.js", \
     "--outputTransport", "streamableHttp", \
     "--stateful", \
     "--port", "3000", \
     "--healthEndpoint", "/health"]
