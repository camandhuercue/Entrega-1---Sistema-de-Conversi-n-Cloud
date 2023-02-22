#!/bin/bash
celery -A tasks worker -l info &
python schedule.py