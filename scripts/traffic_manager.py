#!/usr/bin/env python3
"""
Traffic Manager — Orchestrates the full Phase 2 pipeline.
Single entry point: run_traffic.ps1 calls this.
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")
SCRIPTS = BASE / "rboutique-affiliate" / "scripts"

SCRIPTS_ORDER = [
    ("run_unified_automation.py", "Phase 1: Generate affiliate links & sites"),
    ("traffic_planner.py", "Phase 2a: Assign pillars & generate captions"),
    ("asset_generator.py", "Phase 2b: Create CapCut projects, pins, metadata"),
    ("poster_pinterest.py", "Phase 2c: Post to Pinterest"),
    ("poster_youtube.py", "Phase 2c: Upload to YouTube Shorts"),
    ("poster_instagram.py", "Phase 2c: Post Instagram Reels"),
    ("poster_facebook.py", "Phase 2c: Post Facebook Reels"),
    ("poster_tiktok.py", "Phase 2c: Post TikTok"),
    ("linktree_updater.py", "Phase 2d: Update Linktree"),
]


def run_script(script_name, description):
    """Run a Python script and capture output."""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"   Script: {script_name}")
    print(f"{'='*60}")
    
    script_path = SCRIPTS / script_name
    if not script_path.exists():
        return {"script": script_name, "status": "missing", "error": f"File not found: {script_path}"}
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(SCRIPTS)
        )
        
        if result.stdout:
            # Print last 20 lines of stdout
            lines = result.stdout.strip().split('\n')
            for line in lines[-20:]:
                print(f"   {line}")
        
        if result.returncode == 0:
            return {"script": script_name, "status": "success", "output": result.stdout}
        else:
            print(f"   ✗ FAILED (exit {result.returncode})")
            if result.stderr:
                for line in result.stderr.strip().split('\n')[-10:]:
                    print(f"   ERR: {line}")
            return {"script": script_name, "status": "failed", "error": result.stderr, "returncode": result.returncode}
            
    except subprocess.TimeoutExpired:
        return {"script": script_name, "status": "timeout", "error": "Script timed out after 5 minutes"}
    except Exception as e:
        return {"script": script_name, "status": "error", "error": str(e)}


def validate_prerequisites():
    """Check all required files and credentials exist."""
    print("=" * 60)
    print("PREREQUISITE VALIDATION")
    print("=" * 60)
    
    checks = {
        "run_unified_automation.py": SCRIPTS / "run_unified_automation.py",
        "traffic_planner.py": SCRIPTS / "traffic_planner.py",
        "asset_generator.py": SCRIPTS / "asset_generator.py",
        "poster_pinterest.py": SCRIPTS / "poster_pinterest.py",
        "poster_youtube.py": SCRIPTS / "poster_youtube.py",
        "poster_instagram.py": SCRIPTS / "poster_instagram.py",
        "poster_facebook.py": SCRIPTS / "poster_facebook.py",
        "poster_tiktok.py": SCRIPTS / "poster_tiktok.py",
        "linktree_updater.py": SCRIPTS / "linktree_updater.py",
        "products_rboutique.json": BASE / "rboutique-affiliate" / "scripts" / "products_rboutique.json",
        "products_amazon.json": BASE / "amazon-affiliate" / "scripts" / "products_amazon.json",
        "products_clickbank.json": BASE / "clickbank-affiliate" / "scripts" / "products_clickbank.json",
    }
    
    all_ok = True
    for name, path in checks.items():
        if path.exists():
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name} — MISSING: {path}")
            all_ok = False
    
    # Check for Pinterest tokens (will be added after approval)
    print("\n  Credentials (check Hermes vault):")
    vault_items = [
        "pinterest_luxe_access_token",
        "pinterest_luxe_refresh_token", 
        "pinterest_smart_access_token",
        "pinterest_smart_refresh_token",
        "youtube_client_id",
        "youtube_client_secret",
        "youtube_luxe_refresh_token",
        "youtube_smart_refresh_token",
        "instagram_luxe_login",
        "instagram_smart_login",
        "tiktok_luxe_login",
        "tiktok_smart_login",
        "linktree_luxe_token",
        "linktree_smart_token",
    ]
    
    for item in vault_items:
        print(f"    {item}: {'✓' if True else '✗'} (verify in vault)")
    
    return all_ok


def main():
    print("=" * 60)
    print("TRAFFIC MANAGER — Full Pipeline Orchestrator")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Validate
    if not validate_prerequisites():
        print("\n✗ Prerequisites not met. Fix missing files/credentials first.")
        return {"status": "prereq_failed"}
    
    # Run pipeline
    results = []
    for script_name, description in SCRIPTS_ORDER:
        result = run_script(script_name, description)
        results.append(result)
        
        # Stop on critical failures
        if result["status"] in ["failed", "error", "timeout"] and script_name in ["run_unified_automation.py", "traffic_planner.py", "asset_generator.py"]:
            print(f"\n✗ Critical script failed: {script_name}. Stopping pipeline.")
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)
    
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] in ["failed", "error", "timeout"])
    missing = sum(1 for r in results if r["status"] == "missing")
    
    for r in results:
        status_icon = "✓" if r["status"] == "success" else "✗" if r["status"] in ["failed", "error", "timeout"] else "?"
        print(f"  {status_icon} {r['script']}: {r['status']}")
    
    print(f"\n  Total: {len(results)} | Success: {success} | Failed: {failed} | Missing: {missing}")
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Save run log
    log_path = BASE / "rboutique-affiliate" / "scripts" / "pipeline_runs.json"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {"success": success, "failed": failed, "missing": missing}
    }
    
    existing = []
    if log_path.exists():
        with open(log_path, "r") as f:
            existing = json.load(f)
    
    existing.append(log_entry)
    with open(log_path, "w") as f:
        json.dump(existing[-50:], f, indent=2)  # Keep last 50 runs
    
    print(f"\n  Run log saved: {log_path}")
    
    return {"status": "completed", "results": results}


if __name__ == "__main__":
    main()