#!/bin/bash
python contracts/datamanagement/main.py 1 2 3 4 5 6 7 8 9 10
python /home/ubuntu/contracts/datamanagement/daily_linker.py
python /home/ubuntu/contracts/datamanagement/emailer.py
python /home/ubuntu/contracts/datamanagement/backup.py