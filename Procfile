web: gunicorn myproject.wsgi --timeout 15000000
celery: celery -A myproject worker -B --loglevel=info