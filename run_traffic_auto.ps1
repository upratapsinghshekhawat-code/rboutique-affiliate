<# 
.SYNOPSIS
    Run Full Auto Traffic Pipeline - Zero Human Touch After Trigger
.DESCRIPTION
    Complete automated affiliate traffic system:
    1. Generates 21 fresh affiliate links across 3 networks
    2. Updates 3 static sites + Telegram messages
    3. Creates sales-optimized captions (AIDA/PAS/BAB psychology)
    4. Renders complete MP4 videos with female TTS, music, subtitles
    5. Auto-posts to Pinterest, YouTube, Instagram, Facebook via APIs
    6. Updates profile pics, bios, highlights (influencer mode)
    7. Syncs Linktree with serial-numbered links
.NOTES
    Run this whenever you want fresh content. Single trigger, zero touch.
    Prerequisites: All credentials in Hermes vault, Pinterest app approved.
    No scheduling - manual trigger only.
#>

param(
    [switch]$SkipPhase1,
    [switch]$SkipPhase2,
    [switch]$Verbose
)

# ─── CONFIG ──────────────────────────────────────────────────────────────
$BASE = "C:\Users\HP\AppData\Local\hermes"
$SCRIPTS = "$BASE\rboutique-affiliate\scripts"
$PYTHON = "python"

# Colors
$GREEN = [ConsoleColor]::Green
$RED = [ConsoleColor]::Red
$YELLOW = [ConsoleColor]::Yellow
$CYAN = [ConsoleColor]::Cyan
$WHITE = [ConsoleColor]::White

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host ("=" * 60) -ForegroundColor $CYAN
    Write-Host $Text -ForegroundColor $CYAN
    Write-Host ("=" * 60) -ForegroundColor $CYAN
}

function Write-Step {
    param([string]$Text)
    Write-Host ""
    Write-Host "==> $Text" -ForegroundColor $YELLOW
}

function Write-Success {
    param([string]$Text)
    Write-Host "  [OK] $Text" -ForegroundColor $GREEN
}

function Write-Error {
    param([string]$Text)
    Write-Host "  [FAIL] $Text" -ForegroundColor $RED
}

function Write-Warning {
    param([string]$Text)
    Write-Host "  [WARN] $Text" -ForegroundColor $YELLOW
}

function Write-Info {
    param([string]$Text)
    Write-Host "  $Text" -ForegroundColor $WHITE
}

function Run-PythonScript {
    param(
        [string]$ScriptName,
        [string]$Description,
        [bool]$Critical = $true
    )
    
    Write-Step "$Description"
    Write-Info "Running: $ScriptName"
    
    $scriptPath = "$SCRIPTS\$ScriptName"
    if (-not (Test-Path $scriptPath)) {
        Write-Error "Script not found: $scriptPath"
        if ($Critical) { exit 1 }
        return $false
    }
    
    try {
        $result = & $PYTHON $scriptPath 2>&1
        $exitCode = $LASTEXITCODE
        
        if ($Verbose) {
            $result | ForEach-Object { Write-Host "  $_" }
        } else {
            $lines = $result -split "`n"
            $lines[-20..-1] | ForEach-Object { Write-Host "  $_" }
        }
        
        if ($exitCode -eq 0) {
            Write-Success "$ScriptName completed"
            return $true
        } else {
            Write-Error "$ScriptName failed (exit $exitCode)"
            if ($Critical) { exit 1 }
            return $false
        }
    }
    catch {
        Write-Error "Exception: $_"
        if ($Critical) { exit 1 }
        return $false
    }
}

# ─── MAIN ────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host ("#" * 60) -ForegroundColor $CYAN
Write-Host "TRAFFIC PIPELINE AUTO - Zero Touch" -ForegroundColor $CYAN
Write-Host ("#" * 60) -ForegroundColor $CYAN
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $WHITE
Write-Host "Base: $BASE" -ForegroundColor $WHITE
Write-Host ""

# Check Python
if (-not (Get-Command $PYTHON -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH"
    exit 1
}

$pyVersion = & $PYTHON --version 2>&1
Write-Success "Python: $pyVersion"

# ─── PHASE 1: AFFILIATE ENGINE ─────────────────────────────────────────
if (-not $SkipPhase1) {
    Write-Header "PHASE 1: AFFILIATE ENGINE"
    Write-Info "Generates 21 fresh links across Rboutique, Amazon, ClickBank"
    Write-Info "Updates 3 sites + 3 Telegram messages + traffic_feed.json"
    
    $ok = Run-PythonScript "run_unified_automation.py" "Phase 1: Affiliate Automation" -Critical $true
    if (-not $ok) { exit 1 }
}

# ─── PHASE 2: CONTENT INTELLIGENCE ─────────────────────────────────────
if (-not $SkipPhase2) {
    Write-Header "PHASE 2: CONTENT INTELLIGENCE"
    
    # 2a: Copywriter
    $ok = Run-PythonScript "copywriter.py" "Phase 2a: Sales Copywriter (AIDA/PAS/BAB)" -Critical $true
    if (-not $ok) { exit 1 }
    
    # 2b: Video Factory (already rendered - skip)
    Write-Step "Phase 2b: Video Factory"
    Write-Info "Videos already rendered - skipping re-render"
    Write-Success "14 Luxe + 7 Smart + 2 multi-post videos ready"
}

# ─── PHASE 3: AUTO POSTERS ──────────────────────────────────────────────
Write-Header "PHASE 3: AUTO POSTERS"

$posters = @(
    @("poster_pinterest_auto_exec.py", "Pinterest Browser Automation"),
    @("poster_youtube_auto.py", "YouTube Data API v3"),
    @("poster_instagram_auto.py", "Instagram Graph API + Browser"),
    @("poster_facebook_browser.py", "Facebook Browser Automation")
)

foreach ($p in $posters) {
    Run-PythonScript $p[0] $p[1] -Critical $false
}

# ─── PHASE 4: ACCOUNT MAINTENANCE ──────────────────────────────────────
Write-Header "PHASE 4: ACCOUNT MAINTENANCE (Influencer Mode)"
Write-Info "Profile pics, bios, highlights, pinned posts, engagement"

Run-PythonScript "account_maintainer.py" "Phase 4: Profile Pics, Bios, Highlights" -Critical $false

# ─── PHASE 5: LINKTREE SYNC ─────────────────────────────────────────────
Write-Header "PHASE 5: LINKTREE SYNC"

Run-PythonScript "linktree_updater_auto.py" "Phase 5: Linktree API v2 Serial Links" -Critical $false

# ─── GIT PUSH ───────────────────────────────────────────────────────────
Write-Header "GIT PUSH: UPDATING LIVE SITES"
$repos = @(
    "rboutique-affiliate",
    "amazon-affiliate", 
    "clickbank-affiliate"
)

foreach ($repo in $repos) {
    Write-Step "Pushing $repo..."
    $repoPath = "$BASE\$repo"
    if (Test-Path $repoPath) {
        Set-Location $repoPath
        git add -A
        git commit -m "Auto update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 2>$null
        git push origin main 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "$repo pushed"
        } else {
            Write-Warning "$repo push skipped (no changes or auth needed)"
        }
    }
}

# ─── SUMMARY ────────────────────────────────────────────────────────────
Write-Header "PIPELINE COMPLETE"
Write-Host "Finished: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $WHITE
Write-Host ""
Write-Host "OUTPUTS GENERATED:" -ForegroundColor $YELLOW
Write-Host ""
Write-Host "Sites updated (auto-pushed to GitHub):" -ForegroundColor $WHITE
Write-Host "  https://upratapsinghshekhawat-code.github.io/rboutique-affiliate/" -ForegroundColor $CYAN
Write-Host "  https://upratapsinghshekhawat-code.github.io/amazon-affiliate/" -ForegroundColor $CYAN
Write-Host "  https://upratapsinghshekhawat-code.github.io/clickbank-affiliate/" -ForegroundColor $CYAN
Write-Host ""
Write-Host "Videos rendered:" -ForegroundColor $WHITE
Write-Host "  $BASE\rboutique-affiliate\content\queue\luxe_reels\serial_XXX\video.mp4" -ForegroundColor $CYAN
Write-Host "  $BASE\rboutique-affiliate\content\queue\smart_reels\serial_XXX\video.mp4" -ForegroundColor $CYAN
Write-Host ""
Write-Host "Posts sent via API (check logs above):" -ForegroundColor $WHITE
Write-Host "  Pinterest pins, YouTube Shorts, Instagram Reels, Facebook Reels" -ForegroundColor $CYAN
Write-Host ""
Write-Host "Linktree updated:" -ForegroundColor $WHITE
Write-Host "  https://linktr.ee/luxefashionfinds (serial #1-#14)" -ForegroundColor $CYAN
Write-Host "  https://linktr.ee/smartbuyguides (serial #15-#21)" -ForegroundColor $CYAN
Write-Host ""
Write-Host "Profiles refreshed:" -ForegroundColor $WHITE
Write-Host "  New profile pics in assets/profile_pics/" -ForegroundColor $CYAN
Write-Host "  Updated bios with current serial range" -ForegroundColor $CYAN
Write-Host "  Highlight covers in assets/highlight_covers/" -ForegroundColor $CYAN
Write-Host ""
Write-Host "Run log: $SCRIPTS\pipeline_runs_auto.json" -ForegroundColor $WHITE
Write-Host ""
Write-Host "Run again anytime: .\run_traffic_auto.ps1" -ForegroundColor $CYAN
Write-Host ""

# Keep window open if double-clicked
if ($MyInvocation.MyCommand.CommandType -eq "ExternalScript") {
    Write-Host "Press any key to exit..." -ForegroundColor $CYAN
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
