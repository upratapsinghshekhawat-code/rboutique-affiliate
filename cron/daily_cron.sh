# Rboutique Affiliate Cron — Daily Automation
# Runs: Every day at 09:00 UTC
# Action: Refresh affiliate links + publish new AI content + push Telegram
0 9 * * * /usr/bin/bash /c/Users/HP/AppData/Local/hermes/rboutique-affiliate/generate_link.sh >> /c/Users/HP/AppData/Local/hermes/rboutique-affiliate/cron/daily.log 2>&1
# Weekly (Sunday 10:00): Check raktun dashboard for commission updates
0 10 * * 0 echo "Check raktun dashboard for 6% commission updates — SID 4386419, MID 52880"
