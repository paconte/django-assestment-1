(gunicorn abacum.asgi:application --user www-data --bind 0.0.0.0:8010 --workers 3 -k uvicorn.workers.UvicornWorker) &
nginx -g "daemon off;"
