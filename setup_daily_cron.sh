#\!/bin/bash
# Setup Daily Automated Video Generation
# Configures cron jobs to run all 4 formats at optimal times

WISEVIRGIN_DIR="/root/wisevirgin"

echo "Setting up WiseVirgin Daily Automation..."
echo "=========================================="

# Make all runner scripts executable
chmod +x "$WISEVIRGIN_DIR/run_shorts_daily.py"
chmod +x "$WISEVIRGIN_DIR/run_medium_daily.py"
chmod +x "$WISEVIRGIN_DIR/run_extended_daily.py"
chmod +x "$WISEVIRGIN_DIR/run_sleep_daily.py"

# Backup existing crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

# Create new crontab entries
echo "Adding cron jobs..."

# Remove any existing WiseVirgin cron jobs
crontab -l 2>/dev/null | grep -v "wisevirgin" | grep -v "run_.*_daily.py" > /tmp/crontab_new.txt || true

# Add new cron jobs
cat >> /tmp/crontab_new.txt << 'EOFCRON'

# WiseVirgin Daily Automated Video Generation
# Shorts - 6:00 AM daily (morning inspiration, viral testing)
0 6 * * * cd /root/wisevirgin && /usr/bin/python3 run_shorts_daily.py >> logs/cron_shorts.log 2>&1

# Medium - 12:00 PM daily (midday meditation break)
0 12 * * * cd /root/wisevirgin && /usr/bin/python3 run_medium_daily.py >> logs/cron_medium.log 2>&1

# Extended - 6:00 PM daily (evening deep meditation)
0 18 * * * cd /root/wisevirgin && /usr/bin/python3 run_extended_daily.py >> logs/cron_extended.log 2>&1

# Sleep - 9:00 PM daily (bedtime sleep content)
0 21 * * * cd /root/wisevirgin && /usr/bin/python3 run_sleep_daily.py >> logs/cron_sleep.log 2>&1
EOFCRON

# Install new crontab
crontab /tmp/crontab_new.txt

echo ""
echo "✅ Cron jobs installed successfully\!"
echo ""
echo "Schedule:"
echo "  6:00 AM - Shorts (60s)"
echo " 12:00 PM - Medium (2hr)"
echo "  6:00 PM - Extended (3hr)"
echo "  9:00 PM - Sleep (8hr)"
echo ""
echo "Logs:"
echo "  logs/cron_shorts.log"
echo "  logs/cron_medium.log"
echo "  logs/cron_extended.log"
echo "  logs/cron_sleep.log"
echo ""
