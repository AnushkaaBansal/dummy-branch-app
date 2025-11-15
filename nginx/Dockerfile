FROM nginx:alpine

# Remove default configuration
RUN rm -f /etc/nginx/conf.d/default.conf

# Install wget for health checks
RUN apk add --no-cache wget

# Create log directory
RUN mkdir -p /var/log/nginx/app \
    && touch /var/log/nginx/app/access.log \
    && touch /var/log/nginx/app/error.log \
    && chown -R nginx:nginx /var/log/nginx/app

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
