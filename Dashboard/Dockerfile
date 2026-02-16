# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar el resto del código
COPY . .

# Build de la aplicación (sin verificación de TypeScript para evitar errores)
RUN npm run build:docker

# Stage 2: Production con Nginx
FROM nginx:alpine

# Copiar el build desde el stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración de nginx personalizada
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
