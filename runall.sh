#!/bin/bash

gnome-terminal 	--tab -e "bash -c \"source /home/a1101x/projects/mt/server_venv/bin/activate;
			 cd /home/a1101x/projects/mt/mt_server/; pip install -r requirements.txt; 
			 python manage.py migrate; python manage.py runserver; /bin/bash;\"" \
		--tab -e "bash -c \"sleep 4; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; pip install -r requirements.txt; 
			 python manage.py migrate; python manage.py runserver 8001; /bin/bash;\"" \
		--tab -e "bash -c \"sleep 8; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; 
			 celery -A mt_workers worker -Q default --concurrency=16 -l info --hostname=default@%h; 
			 /bin/bash;\"" \
		--tab -e "bash -c \"sleep 12; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; 
			 celery -A mt_workers worker -Q elastic_write_user --concurrency=24 -l info --hostname=elastic_write_user@%h;
			 /bin/bash;\"" \
		--tab -e "bash -c \"sleep 16; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; 
			 celery -A mt_workers worker -Q elastic_read_user --concurrency=4 -l info --hostname=elastic_read_user@%h;
			 /bin/bash;\"" \
		--tab -e "bash -c \"sleep 20; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; celery -A mt_workers beat -l info;
			 /bin/bash;\"" \
		--tab -e "bash -c \"sleep 24; source /home/a1101x/projects/mt/workers_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_workers/; flower -A mt_workers --port=5555;
			 /bin/bash;\"" \
		--tab -e "bash -c \"sleep 28; source /home/a1101x/projects/mt/sockets_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_sockets/; pip install -r requirements.txt; 
			 daphne apps.core.asgi:channel_layer --port 8002; /bin/bash;\"" \
		--tab -e "bash -c \"sleep 32; source /home/a1101x/projects/mt/sockets_venv/bin/activate; 
			 cd /home/a1101x/projects/mt/mt_sockets/; python manage.py runworker --threads 16 
			--only-channels \"websocket*\"; /bin/bash;\"" 
