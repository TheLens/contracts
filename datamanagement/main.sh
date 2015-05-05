#!/bin/bash
python contracts/datamanagement/main.py
python /home/ubuntu/contracts/datamanagement/daily_linker.py
python /home/ubuntu/contracts/datamanagement/emailer.py
python /home/ubuntu/contracts/datamanagement/backup.py