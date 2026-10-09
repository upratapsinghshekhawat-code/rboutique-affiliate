#!/usr/bin/env python3
"""
Traffic Manager AUTO — Full zero-touch orchestrator.
Single entry point: run_traffic_auto.ps1 calls this.
Runs Phase 1 → Phase 2 → All auto-posters → Account maintenance → Linktree sync.
"""
import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
SCRIPTS = BASE / "rboutique-affiliate" / "scripts"

# ─── PIPELINE STEPS ──────────────────────────────────────────────────────
AUTO_PIPELINE = [
    # Phase 1: Affiliate Engine
    ("run_unified_automation.py", "Phase 1: Affiliate Engine (21 links, 3 sites, feed)", True),
    
    # Phase 2: Content Intelligence
    ("copywriter.py", "Phase 2a: Sales Copywriter (AIDA/PAS/BAB captions)", True),
    ("video_factory.py", "Phase 2b: Video Factory (MP4 + TTS + Music + Subs)", True),
    
    # Phase 3: Auto-Posters (Parallel-ready)
    ("poster_pinterest_auto_exec.py", "Phase 3a: Pinterest Browser Automation (Generates Steps)", True),
    ("poster_youtube_auto.py", "Phase 3b: YouTube Data API v3", False),
    ("poster_instagram_auto.py", "Phase 3c: Instagram Graph API + Browser", False),
    ("poster_facebook_browser.py", "Phase 3d: Facebook Browser Automation", True),
    
    # Phase 4: Account Maintenance (Influencer Mode)
    ("account_maintainer.py", "Phase 4: Profile Pics, Bios, Highlights, Pinned", False),
    
    # Phase 5: Linktree Sync
    ("linktree_updater_auto.py", "Phase 5: Linktree API v2 Serial Links", False),
]


def run_script(script_name, description, critical=True):
    """Run a Python script and capture output."""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"   Script: {script_name}")
    print(f"{'='*60}")
    
    script_path = SCRIPTS / script_name
    if not script_path.exists():
        msg = f"File not found: {script_path}"
        print(f"   ✗ {msg}")
        if critical:
            return {"script": script_name, "status": "missing", "error": msg}
        return {"script": script_name, "status": "skipped", "error": msg}
    
    # Set up environment for credentials
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SCRIPTS)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 min per script
            cwd=str(SCRIPTS),
            env=env
        )
        
        if result.stdout:
            # Print last 30 lines
            lines = result.stdout.strip().split('\n')
            for line in lines[-30:]:
                print(f"   {line}")
        
        if result.returncode == 0:
            print(f"   ✓ {script_name} completed")
            return {"script": script_name, "status": "success", "output": result.stdout}
        else:
            print(f"   ✗ {script_name} failed (exit {result.returncode})")
            if result.stderr:
                for line in result.stderr.strip().split('\n')[-15:]:
                    print(f"   ERR: {line}")
            if critical:
                return {"script": script_name, "status": "failed", "error": result.stderr, "returncode": result.returncode, "critical": True}
            return {"script": script_name, "status": "failed", "error": result.stderr, "returncode": result.returncode}
            
    except subprocess.TimeoutExpired:
        msg = "Script timed out after 10 minutes"
        print(f"   ✗ {msg}")
        if critical:
            return {"script": script_name, "status": "timeout", "error": msg, "critical": True}
        return {"script": script_name, "status": "timeout", "error": msg}
    except Exception as e:
        msg = f"Exception: {e}"
        print(f"   ✗ {msg}")
        if critical:
            return {"script": script_name, "status": "error", "error": msg, "critical": True}
        return {"script": script_name, "status": "error", "error": msg}


def validate_prerequisites():
    """Check all required files and credentials exist."""
    print("=" * 60)
    print("PREREQUISITE VALIDATION")
    print("=" * 60)
    
    required_files = [
        "run_unified_automation.py",
        "copywriter.py",
        "video_factory.py",
        "poster_pinterest_auto.py",
        "poster_youtube_auto.py",
        "poster_instagram_auto.py",
        "poster_facebook_auto.py",
        "account_maintainer.py",
        "linktree_updater_auto.py",
        "products_rboutique.json",
        "products_amazon.json",
        "products_clickbank.json",
    ]
    
    all_ok = True
    for name in required_files:
        path = SCRIPTS / name if name.endswith(".py") else BASE / "rboutique-affiliate" / "scripts" / name
        if path.exists():
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} — MISSING: {path}")
            all_ok = False
    
    # Check credentials (environment variables from vault)
    print("\n  Credentials (from Hermes vault → environment):")
    creds = [
        ("PINTEREST_LUXE_ACCESS_TOKEN", "Pinterest Luxe"),
        ("PINTEREST_LUXE_REFRESH_TOKEN", "Pinterest Luxe Refresh"),
        ("PINTEREST_LUXE_CLIENT_ID", "Pinterest Luxe Client ID"),
        ("PINTEREST_LUXE_CLIENT_SECRET", "Pinterest Luxe Client Secret"),
        ("PINTEREST_SMART_ACCESS_TOKEN", "Pinterest Smart"),
        ("PINTEREST_SMART_REFRESH_TOKEN", "Pinterest Smart Refresh"),
        ("PINTEREST_SMART_CLIENT_ID", "Pinterest Smart Client ID"),
        ("PINTEREST_SMART_CLIENT_SECRET", "Pinterest Smart Client Secret"),
        ("YOUTUBE_CLIENT_ID", "YouTube Client ID"),
        ("YOUTUBE_CLIENT_SECRET", "YouTube Client Secret"),
        ("YOUTUBE_LUXE_REFRESH_TOKEN", "YouTube Luxe Refresh"),
        ("YOUTUBE_SMART_REFRESH_TOKEN", "YouTube Smart Refresh"),
        ("INSTAGRAM_LUXE_ACCESS_TOKEN", "Instagram Luxe"),
        ("INSTAGRAM_LUXE_USER_ID", "Instagram Luxe User ID"),
        ("INSTAGRAM_SMART_ACCESS_TOKEN", "Instagram Smart"),
        ("INSTAGRAM_SMART_USER_ID", "Instagram Smart User ID"),
        ("FACEBOOK_LUXE_PAGE_TOKEN", "Facebook Luxe Page Token"),
        ("FACEBOOK_LUXE_PAGE_ID", "Facebook Luxe Page ID"),
        ("FACEBOOK_SMART_PAGE_TOKEN", "Facebook Smart Page Token"),
        ("FACEBOOK_SMART_PAGE_ID", "Facebook Smart Page ID"),
        ("LINKTREE_LUXE_TOKEN", "Linktree Luxe"),
        ("LINKTREE_SMART_TOKEN", "Linktree Smart"),
    ]
    
    for env_var, label in creds:
        # In production, these come from Hermes vault injected at runtime
        # For now, just check if set
        status = "✓" if os.environ.get(env_var) else "⚠ (will use browser fallback)"
        print(f"    {label}: {status}")
    
    return all_ok


def inject_vault_credentials():
    """Inject credentials from Hermes vault into environment.
    In production, this would call Hermes vault API.
    For now, we document what needs to be set."""
    print("""
═══════════════════════════════════════════════════════
VAULT CREDENTIAL INJECTION
═══════════════════════════════════════════════════════

Before running, ensure these are in Hermes vault (Settings → Passwords & Logins):

PINTEREST:
  pinterest_luxe_client_id, pinterest_luxe_client_secret
  pinterest_luxe_access_token, pinterest_luxe_refresh_token
  pinterest_smart_client_id, pinterest_smart_client_secret
  pinterest_smart_access_token, pinterest_smart_refresh_token

YOUTUBE:
  youtube_client_id, youtube_client_secret
  youtube_luxe_refresh_token, youtube_smart_refresh_token

INSTAGRAM:
  instagram_luxe_login (username + password)
  instagram_smart_login (username + password)
  → Also need: INSTAGRAM_LUXE_USER_ID, INSTAGRAM_SMART_USER_ID
  → And long-lived access tokens (from Graph API)

FACEBOOK:
  facebook_luxe_page_login (page access token + page ID)
  facebook_smart_page_login

LINKTREE:
  linktree_luxe_token, linktree_smart_token

These will be injected as environment variables at runtime.
""")


def main():
    print("=" * 60)
    print("TRAFFIC MANAGER AUTO — Zero-Touch Full Pipeline")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base: {BASE}")
    
    # Show vault injection info
    inject_vault_credentials()
    
    # Validate
    if not validate_prerequisites():
        print("\n⚠ Some prerequisites missing. Pipeline will attempt anyway with fallbacks.")
    
    # Run pipeline
    results = []
    critical_failed = False
    
    for script_name, description, critical in AUTO_PIPELINE:
        if critical_failed and critical:
            print(f"\n⏭ Skipping {script_name} (critical dependency failed)")
            results.append({"script": script_name, "status": "skipped", "reason": "critical_failed"})
            continue
        
        result = run_script(script_name, description, critical)
        results.append(result)
        
        if result.get("critical") and result["status"] in ["failed", "error", "timeout", "missing"]:
            critical_failed = True
            print(f"\n🛑 Critical failure in {script_name}. Stopping pipeline.")
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] in ["failed", "error", "timeout"])
    skipped = sum(1 for r in results if r["status"] == "skipped")
    
    for r in results:
        status_icon = {
            "success": "✓",
            "failed": "✗",
            "error": "✗",
            "timeout": "⏱",
            "missing": "?",
            "skipped": "⏭"
        }.get(r["status"], "?")
        print(f"  {status_icon} {r['script']}: {r['status']}")
    
    print(f"\n  Total: {len(results)} | Success: {success} | Failed: {failed} | Skipped: {skipped}")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save run log
    log_path = SCRIPTS / "pipeline_runs_auto.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {"success": success, "failed": failed, "skipped": skipped}
    }
    
    existing = []
    if log_path.exists():
        with open(log_path, "r") as f:
            existing = json.load(f)
    
    existing.append(log_entry)
    with open(log_path, "w") as f:
        json.dump(existing[-50:], f, indent=2)
    
    print(f"\n  Run log saved: {log_path}")
    
    # Next steps for manual parts
    if any(r["status"] in ["failed", "skipped"] for r in results):
        print("""
═══════════════════════════════════════════════════════
MANUAL FOLLOW-UP NEEDED
═══════════════════════════════════════════════════════

Check output above for browser automation instructions:
- Instagram Reels: Follow browser steps from poster_instagram_auto.py
- Facebook Reels: Cross-post from Instagram (enable "Share to Facebook")
- Profile Pics: Upload generated images from assets/profile_pics/
- Highlight Covers: Upload from assets/highlight_covers/

Run again after manual steps: .\\run_traffic_auto.ps1
""")
    
    return {"status": "completed" if not critical_failed else "partial", "results": results}


if __name__ == "__main__":
    main()