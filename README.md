# FOR DEVELOPMENT
```
change runall.sh and run it: ./runall.sh
```

# mt_server

Python 3
```
virtualenv server_venv -p python3
```
```
pip install -r mt_server/requirements.txt
```
```
cd mt_server
```
```
python manage.py migrate
```
```
python manage.py runserver
```

# mt_workers

Python 3
```
virtualenv workers_venv -p python3
```
```
pip install -r mt_workers/requirements.txt
```
```
cd mt_workers
```
```
python manage.py runserver 8001
```

second/third/fourth/fifth terminal
```
different workers\queues
celery -A mt_workers worker -Q default --concurrency=2 -l info --hostname=default@%h
celery -A mt_workers worker -Q elastic_write_user --concurrency=2 -l info --hostname=elastic_write_user@%h
celery -A mt_workers worker -Q elastic_read_user --concurrency=1 -l info --hostname=elastic_read_user@%h
celery -A mt_workers beat -l info
```

sixth terminal
```
flower -A mt_workers --port=5555
```

# mt_sockets

Python 3
```
virtualenv sockets_venv -p python3
```
```
pip install -r mt_sockets/requirements.txt
```
```
cd mt_sockets
```
```
daphne apps.core.asgi:channel_layer --port 8002
```

second terminal
```
python manage.py runworker --threads 2 --only-channels "websocket*"
```

# some tests
```
python manage.py test apps
```
