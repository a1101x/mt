#!/bin/bash

gnome-terminal 	--tab -e "bash -c \"source /home/a1101x/projects/mt/server_venv/bin/activate;
			 cd /home/a1101x/projects/mt/mt_server/; pip install -r requirements.txt; 
			 python manage.py migrate; python manage.py runserver;\"" \
		--tab -e "bash -c \"sleep 4; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; pip install -r requirements.txt; 
			 python manage.py runserver 8001;\"" \
		--tab -e "bash -c \"sleep 8; source /home/a1101x/projects/mt/sockets_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_sockets/; pip install -r requirements.txt; 
			 daphne apps.core.asgi:channel_layer --port 8002;\"" \
		--tab -e "bash -c \"sleep 14; source /home/a1101x/projects/mt/sockets_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_sockets/; python manage.py runworker;\"" \
		--tab -e "bash -c \"sleep 16; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; 
			 celery -A mt_workers worker --concurrency=4 -l info;\"" \
		--tab -e "bash -c \"sleep 20; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; flower -A mt_workers --port=5555;\"" 

