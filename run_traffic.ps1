<# 
.SYNOPSIS
    Run Traffic Pipeline - Full Phase 1 + Phase 2 automation
.DESCRIPTION
    Single manual trigger for the entire affiliate traffic pipeline:
    1. Generates fresh affiliate links across 3 networks (Rboutique, Amazon, ClickBank)
    2. Updates 3 static sites + 3 Telegram messages
    3. Creates content plan with serial numbers, pillars, captions
    4. Generates CapCut projects, Pinterest pins, YouTube metadata
    5. Provides posting instructions for all 5 platforms × 2 accounts
    6. Updates Linktree with serial-numbered links
.NOTES
    Run this whenever you want fresh content. No scheduling - manual only.
    Prerequisites: All credentials in Hermes vault, Pinterest app approved.
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

# Colors for output
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
    Write-Host "▶ $Text" -ForegroundColor $YELLOW
}

function Write-Success {
    param([string]$Text)
    Write-Host "  ✓ $Text" -ForegroundColor $GREEN
}

function Write-Error {
    param([string]$Text)
    Write-Host "  ✗ $Text" -ForegroundColor $RED
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
            # Show last 15 lines
            $lines = $result -split "`n"
            $lines[-15..-1] | ForEach-Object { Write-Host "  $_" }
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
Write-Host "TRAFFIC PIPELINE — Manual Trigger" -ForegroundColor $CYAN
Write-Host ("#" * 60) -ForegroundColor $CYAN
Write-Host "Started: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $WHITE
Write-Host "Base: $BASE" -ForegroundColor $WHITE
Write-Host ""

# Check Python
if (-not (Get-Command $PYTHON -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found in PATH"
    exit 1
}
Write-Success "Python: $($PYTHON --version 2>&1 | Select-Object -First 1)"

# ─── PHASE 1: AFFILIATE ENGINE ─────────────────────────────────────────
if (-not $SkipPhase1) {
    Write-Header "PHASE 1: AFFILIATE ENGINE"
    Write-Info "Generates 21 fresh links across Rboutique, Amazon, ClickBank"
    Write-Info "Updates 3 sites + 3 Telegram messages + traffic_feed.json"
    
    $ok = Run-PythonScript "run_unified_automation.py" "Phase 1: Affiliate Automation" -Critical $true
    if (-not $ok) { exit 1 }
}

# ─── PHASE 2: TRAFFIC PIPELINE ─────────────────────────────────────────
if (-not $SkipPhase2) {
    Write-Header "PHASE 2: TRAFFIC PIPELINE"
    Write-Info "Creates content plan, assets, and posting instructions"
    
    # 2a: Traffic Planner
    $ok = Run-PythonScript "traffic_planner.py" "Phase 2a: Content Planner" -Critical $true
    if (-not $ok) { exit 1 }
    
    # 2b: Asset Generator
    $ok = Run-PythonScript "asset_generator.py" "Phase 2b: Asset Generator" -Critical $true
    if (-not $ok) { exit 1 }
    
    # 2c: Posters (instruction generators)
    Write-Step "Phase 2c: Posting Instructions"
    
    $scripts = @(
        @("poster_pinterest.py", "Pinterest"),
        @("poster_youtube.py", "YouTube Shorts"),
        @("poster_instagram.py", "Instagram Reels"),
        @("poster_facebook.py", "Facebook Reels"),
        @("poster_tiktok.py", "TikTok")
    )
    
    foreach ($s in $scripts) {
        Run-PythonScript $s[0] "$($s[1]) Poster" -Critical $false
    }
    
    # 2d: Linktree Updater
    Run-PythonScript "linktree_updater.py" "Phase 2d: Linktree Updater" -Critical $false
}

# ─── SUMMARY ───────────────────────────────────────────────────────────
Write-Header "PIPELINE COMPLETE"
Write-Host "Finished: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $WHITE
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor $YELLOW
Write-Host ""
Write-Host "1. PINTEREST: Check $BASE\rboutique-affiliate\content\queue\pinterest_pins\" -ForegroundColor $WHITE
Write-Host "   Upload pin images manually or via API when tokens ready" -ForegroundColor $WHITE
Write-Host ""
Write-Host "2. YOUTUBE: Export CapCut projects from luxe_reels/ & smart_reels/" -ForegroundColor $WHITE
Write-Host "   Upload MP4s + metadata from youtube_shorts/" -ForegroundColor $WHITE
Write-Host ""
Write-Host "3. INSTAGRAM: Export CapCut projects → Post Reels manually" -ForegroundColor $WHITE
Write-Host "   Follow instructions from poster_instagram.py output" -ForegroundColor $WHITE
Write-Host "   Cross-post to Facebook when posting" -ForegroundColor $WHITE
Write-Host ""
Write-Host "4. TIKTOK: Export CapCut projects → Post manually" -ForegroundColor $WHITE
Write-Host "   Follow instructions from poster_tiktok.py output" -ForegroundColor $WHITE
Write-Host ""
Write-Host "5. LINKTREE: Update via API when tokens available" -ForegroundColor $WHITE
Write-Host "   Or manually add serial links at linktr.ee/luxefashionfinds & linktr.ee/smartbuyguides" -ForegroundColor $WHITE
Write-Host ""
Write-Host "6. SITES: Push to GitHub (already done by Phase 1)" -ForegroundColor $WHITE
Write-Host "   Verify: https://upratapsinghshekhawat-code.github.io/rboutique-affiliate/" -ForegroundColor $WHITE
Write-Host "   Verify: https://upratapsinghshekhawat-code.github.io/amazon-affiliate/" -ForegroundColor $WHITE
Write-Host "   Verify: https://upratapsinghshekhawat-code.github.io/clickbank-affiliate/" -ForegroundColor $WHITE
Write-Host ""
Write-Host "Run again anytime: .\run_traffic.ps1" -ForegroundColor $CYAN
Write-Host ""

# Keep window open if run by double-click
if ($MyInvocation.MyCommand.CommandType -eq "ExternalScript") {
    Write-Host "Press any key to exit..." -ForegroundColor $CYAN
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}