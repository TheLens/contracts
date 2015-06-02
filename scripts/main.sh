#!/bin/bash

# To be run from one level up

echo "Checking the city's purchasing site for new contracts..."
python contracts/lib/check_city.py

echo "Finding links between things..."
python contracts/lib/daily_linker.py

echo "Sending an email with found links..."
python contracts/lib/emailer.py

echo "Creating backups..."
python contracts/lib/backup.py
