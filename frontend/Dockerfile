# ================================
# STAGE 1: Dependencies
# ================================
FROM node:20-alpine AS deps

WORKDIR /app

# Instalar dependencias basadas en el gestor de paquetes preferido
COPY package*.json ./
RUN npm ci

# ================================
# STAGE 2: Build Next.js Application
# ================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar dependencias instaladas
COPY --from=deps /app/node_modules ./node_modules

# Copiar archivos del proyecto
COPY . .

# Argumentos de build para variables de entorno
ARG VITE_API_URL
ARG NODE_ENV=production

# Establecer variables de entorno para el build
ENV NEXT_PUBLIC_API_URL=${VITE_API_URL}
ENV NODE_ENV=${NODE_ENV}
ENV NEXT_TELEMETRY_DISABLED=1

# Construir la aplicación Next.js
RUN npm run build

# ================================
# STAGE 3: Production Runner con Next.js standalone
# ================================
FROM node:20-alpine AS runner

WORKDIR /app

# No ejecutar como root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copiar archivos públicos
COPY --from=builder /app/public ./public

# Copiar el servidor standalone de Next.js
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Iniciar el servidor Next.js
CMD ["node", "server.js"]
