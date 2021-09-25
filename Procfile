web: gunicorn myproject.wsgi --timeout 15000000
worker: celery -A myproject worker -B --loglevel=info