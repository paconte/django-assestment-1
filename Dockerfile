FROM python:3.9-bullseye

# install nginx
RUN apt-get update && apt-get install nginx vim -y --no-install-recommends
COPY nginx/nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# install django
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY abacum /app
COPY abacum/static /app
COPY nginx/start-server.sh /app
RUN chown -R www-data:www-data /app
EXPOSE 8020
STOPSIGNAL SIGTERM
CMD ["/bin/sh", "-c", "/app/start-server.sh"]