#!/usr/bin/env bash
# Manual Affiliate Automation Trigger
# Run this whenever you open your laptop: ./run_affiliate.sh

set -e

BASE="/c/Users/HP/AppData/Local/hermes"
SCRIPTS="$BASE/rboutique-affiliate/scripts"
CRON="$BASE/rboutique-affiliate/cron"

echo "============================================================"
echo "MANUAL AFFILIATE AUTOMATION TRIGGER"
echo "============================================================"
echo "Started: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo ""

# 1. Run unified automation (generates 21 links, updates 3 sites, saves telegram messages)
cd "$SCRIPTS"
echo "[1/4] Running unified automation..."
python run_unified_automation.py
echo ""

# 2. Push rboutique (docs folder for GitHub Pages)
cd "$BASE/rboutique-affiliate"
echo "[2/4] Pushing rboutique-affiliate..."
git add docs/index.html site/index.html telegram_combined.txt telegram_message.txt 2>/dev/null || true
git commit -m "Manual run: $(date -u +'%Y-%m-%d %H:%M UTC') - 21 fresh links" 2>/dev/null || echo "  (no changes to commit)"
git push origin main
echo ""

# 3. Push amazon
cd "$BASE/amazon-affiliate"
echo "[3/4] Pushing amazon-affiliate..."
git add index.html telegram_message.txt 2>/dev/null || true
git commit -m "Manual run: $(date -u +'%Y-%m-%d %H:%M UTC') - 7 fresh links" 2>/dev/null || echo "  (no changes to commit)"
git push origin main
echo ""

# 4. Push clickbank
cd "$BASE/clickbank-affiliate"
echo "[4/4] Pushing clickbank-affiliate..."
git add index.html telegram_message.txt 2>/dev/null || true
git commit -m "Manual run: $(date -u +'%Y-%m-%d %H:%M UTC') - 7 fresh links" 2>/dev/null || echo "  (no changes to commit)"
git push origin main
echo ""

# 5. Trigger n8n workflow (optional - sends Telegram notification + email sequence)
echo "[5/5] Triggering n8n notification..."
curl -s -X POST "http://localhost:5678/webhook/affiliate-run" \
  -H "Content-Type: application/json" \
  -d '{"trigger":"manual","timestamp":"'"$(date -u +"%Y-%m-%dT%H:%M:%SZ")"'"}' >/dev/null 2>&1 || echo "  (n8n webhook not reachable - skipping)"

echo ""
echo "============================================================"
echo "DONE — All 3 sites updated, 21 fresh links live"
echo "Sites:"
echo "  https://upratapsinghshekhawat-code.github.io/rboutique-affiliate/docs/"
echo "  https://upratapsinghshekhawat-code.github.io/amazon-affiliate/"
echo "  https://upratapsinghshekhawat-code.github.io/clickbank-affiliate/"
echo "Telegram: Combined message saved to rboutique-affiliate/telegram_combined.txt"
echo "Completed: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo "============================================================"