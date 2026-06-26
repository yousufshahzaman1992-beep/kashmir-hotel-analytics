#!/bin/bash
PROJECT_DIR="$HOME/kashmir-hotel-analytics"
PYTHON="$HOME/miniconda3/bin/python"
mkdir -p "$PROJECT_DIR/logs"
CRON_JOB="0 0,6,12,18 * * * $PYTHON $PROJECT_DIR/sync_worker.py >> $PROJECT_DIR/logs/sync.log 2>&1"
(crontab -l 2>/dev/null | grep -q "sync_worker.py") && echo "Cron already exists." || {
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "Cron job added - runs at midnight, 6am, 12pm, 6pm daily."
}
crontab -l
