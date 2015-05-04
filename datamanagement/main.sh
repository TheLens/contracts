#!/bin/bash

python contracts/datamanagement/main.py

sleep 3h  #give document cloud 3 hours to process the new files. if by some chance it does not finish by then, the sync script will catch them the next time around

python /home/ubuntu/contracts/datamanagement/lensDocCloudSynch.py
python /home/ubuntu/contracts/datamanagement/daily_linker.py
python /home/ubuntu/contracts/datamanagement/emailer.py
python /home/ubuntu/contracts/datamanagement/backup.py
