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
python manage.py migrate
```
```
python manage.py runserver
```

second terminal
```
celery -A mt_workers worker -l info
```