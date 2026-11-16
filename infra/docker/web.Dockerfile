# Imagen `web` para el compose (en la nube se publica como sitio estático, ADR-0003).
# Contexto: web/.   docker build -f infra/docker/web.Dockerfile -t svca-web web
# Las URL de las APIs se fijan al construir: Vite las incrusta en el JavaScript.
FROM node:22-alpine AS construccion
WORKDIR /web
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
ARG VITE_URL_NUCLEO=http://localhost:8000
ARG VITE_URL_PRONOSTICO=http://localhost:8001
ARG VITE_URL_SIMULADOR=http://localhost:8002
ENV VITE_URL_NUCLEO=$VITE_URL_NUCLEO VITE_URL_PRONOSTICO=$VITE_URL_PRONOSTICO VITE_URL_SIMULADOR=$VITE_URL_SIMULADOR
RUN npm run build

FROM nginxinc/nginx-unprivileged:1.27-alpine
COPY --from=construccion /web/dist /usr/share/nginx/html
# Aplicación de página única: toda ruta desconocida devuelve index.html.
RUN printf 'server {\n  listen 8080;\n  root /usr/share/nginx/html;\n  location / { try_files $uri /index.html; }\n}\n' \
    > /etc/nginx/conf.d/default.conf
EXPOSE 8080
