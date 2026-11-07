FROM nginx:alpine
# NGINX_CONF picks the config: nginx.conf (development, HTTP) or nginx.prod.conf (TLS).
ARG NGINX_CONF=nginx.conf
COPY ${NGINX_CONF} /etc/nginx/nginx.conf
COPY snippets/ /etc/nginx/snippets/
EXPOSE 80 443
