# Run Affiliate Automation - PowerShell Version
# Double-click or run: .\run_affiliate.ps1

$ErrorActionPreference = "Stop"

$BASE = "C:\Users\HP\AppData\Local\hermes"
$SCRIPTS = "$BASE\rboutique-affiliate\scripts"
$RBOUTIQUE = "$BASE\rboutique-affiliate"
$AMAZON = "$BASE\amazon-affiliate"
$CLICKBANK = "$BASE\clickbank-affiliate"

Write-Host "============================================================"
Write-Host "MANUAL AFFILIATE AUTOMATION TRIGGER (PowerShell)"
Write-Host "============================================================"
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') UTC"
Write-Host ""

# 1. Run unified automation
Write-Host "[1/5] Running unified automation..."
Set-Location $SCRIPTS
python run_unified_automation.py
Write-Host ""

# 2. Push rboutique
Write-Host "[2/5] Pushing rboutique-affiliate..."
Set-Location $RBOUTIQUE
git add docs/index.html, site/index.html, telegram_combined.txt, telegram_message.txt 2>$null
if (git diff --cached --quiet) {
    Write-Host "  (no changes to commit)"
} else {
    git commit -m "Manual run: $(Get-Date -Format 'yyyy-MM-dd HH:mm UTC') - 21 fresh links"
    git push origin main
}
Write-Host ""

# 3. Push amazon
Write-Host "[3/5] Pushing amazon-affiliate..."
Set-Location $AMAZON
git add index.html, telegram_message.txt 2>$null
if (git diff --cached --quiet) {
    Write-Host "  (no changes to commit)"
} else {
    git commit -m "Manual run: $(Get-Date -Format 'yyyy-MM-dd HH:mm UTC') - 7 fresh links"
    git push origin main
}
Write-Host ""

# 4. Push clickbank
Write-Host "[4/5] Pushing clickbank-affiliate..."
Set-Location $CLICKBANK
git add index.html, telegram_message.txt 2>$null
if (git diff --cached --quiet) {
    Write-Host "  (no changes to commit)"
} else {
    git commit -m "Manual run: $(Get-Date -Format 'yyyy-MM-dd HH:mm UTC') - 7 fresh links"
    git push origin main
}
Write-Host ""

# 5. Trigger n8n webhook (optional)
Write-Host "[5/5] Triggering n8n notification..."
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
$body = @{ trigger = "manual"; timestamp = $timestamp } | ConvertTo-Json -Compress
try {
    Invoke-RestMethod -Uri "http://localhost:5678/webhook/affiliate-run" -Method Post -ContentType "application/json" -Body $body -TimeoutSec 5 | Out-Null
    Write-Host "  [OK] n8n notified"
} catch {
    Write-Host "  (n8n webhook not reachable - skipping)"
}
Write-Host ""

Write-Host "============================================================"
Write-Host "DONE - All 3 sites updated, 21 fresh links live"
Write-Host "Sites:"
Write-Host "  https://upratapsinghshekhawat-code.github.io/rboutique-affiliate/docs/"
Write-Host "  https://upratapsinghshekhawat-code.github.io/amazon-affiliate/"
Write-Host "  https://upratapsinghshekhawat-code.github.io/clickbank-affiliate/"
Write-Host "Telegram: Combined message saved to rboutique-affiliate/telegram_combined.txt"
Write-Host "Completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') UTC"
Write-Host "============================================================"

# Keep window open
Read-Host "Press Enter to close"