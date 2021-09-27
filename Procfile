web: gunicorn myproject.wsgi --timeout 15000000
celery: celery -A myapp worker -B --loglevel=info