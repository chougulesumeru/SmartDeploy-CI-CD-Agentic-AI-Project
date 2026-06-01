# stage 1:- building stage
FROM nodejs:20-alpine AS builder 

WORKDIR /app

COPY package*.json ./

RUN npm ci --only=production

#stage 2:- production stage

FROM nodejs:20-alpine AS runner

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules

COPY src/ ./src

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \ 
    CMD wget -qO- http://localhost:3000/health || exit 1   

USER node 

CMD ["node", "src/index.js"]

# multi-stage docker builds keep image small.
# The health check instruction lets kubernetes and AI agent know if the app is truly runnig - not just started.