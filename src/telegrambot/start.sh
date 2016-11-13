#!/bin/bash

source venv/bin/activate
./watsonbot.py >> telegram_log.txt 2>&1