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

second terminal
```
celery -A mt_workers worker --concurrency=10 -l info

OR (diff terminals)

celery -A mt_workers worker --loglevel=INFO --concurrency=10 -n worker1@%h
celery -A mt_workers worker --loglevel=INFO --concurrency=10 -n worker2@%h
celery -A mt_workers worker --loglevel=INFO --concurrency=10 -n worker3@%h
```
third terminal
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
python manage.py runworker
```
