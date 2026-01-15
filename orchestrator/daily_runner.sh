#!/bin/bash
# Daily automation runner for WiseVirgin Club USA
# Add to crontab: 0 6 * * * /root/wisevirgin/orchestrator/daily_runner.sh

cd /root/wisevirgin

# Activate venv
source venv/bin/activate

# Run orchestrator
python3 orchestrator/main.py

# Deactivate
deactivate
