#!/usr/bin/env bash
# Unified Affiliate Automation Cron — Daily at 09:00 UTC
# Runs: Rboutique (6%) + Amazon (4-10%) + ClickBank (50-75%)
# Output: 21 tracked links/day → 3 sites + 3 Telegram messages + 1 combined

cd /c/Users/HP/AppData/Local/hermes/rboutique-affiliate/scripts
python3 run_unified_automation.py >> /c/Users/HP/AppData/Local/hermes/rboutique-affiliate/cron/daily.log 2>&1

# Git auto-commit for GitHub Pages (rboutique)
cd /c/Users/HP/AppData/Local/hermes/rboutique-affiliate
git add site/index.html telegram_message.txt telegram_combined.txt
git commit -m "Daily affiliate refresh: $(date -u +'%Y-%m-%d %H:%M UTC') — 21 links" || true
git push origin main || true

# Git auto-commit for Amazon (GitHub Pages at root)
cd /c/Users/HP/AppData/Local/hermes/amazon-affiliate
git add index.html telegram_message.txt
git commit -m "Daily Amazon refresh: $(date -u +'%Y-%m-%d %H:%M UTC') — 7 links" || true
git push origin main || true

# Git auto-commit for ClickBank (GitHub Pages)
cd /c/Users/HP/AppData/Local/hermes/clickbank-affiliate
git add index.html telegram_message.txt
git commit -m "Daily ClickBank refresh: $(date -u +'%Y-%m-%d %H:%M UTC') — 7 links" || true
git push origin main || true

# Weekly commission check (Sunday 10:00 UTC)
# 0 10 * * 0 echo "Check Rakuten dashboard: SID 4386419, MID 52880 (6% commission)" >> /c/Users/HP/AppData/Local/hermes/rboutique-affiliate/cron/daily.log