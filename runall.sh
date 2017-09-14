#!/bin/bash

gnome-terminal --tab -e "bash -c \"
source /home/a1101x/projects/mt/server_venv/bin/activate
cd /home/a1101x/projects/mt/mt_server/
python manage.py runserver\"" --tab -e "bash -c \"
source /home/a1101x/projects/mt/workers_venv/bin/activate
cd /home/a1101x/projects/mt/mt_workers/
python manage.py runserver 8001\"" --tab -e "bash -c \"
source /home/a1101x/projects/mt/workers_venv/bin/activate
cd /home/a1101x/projects/mt/mt_workers/
celery -A mt_workers worker --concurrency=10 -l info\"" --tab -e "bash -c \"
source /home/a1101x/projects/mt/workers_venv/bin/activate
cd /home/a1101x/projects/mt/mt_workers/
flower -A mt_workers --port=5555\"" 

