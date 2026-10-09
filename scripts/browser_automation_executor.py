#!/usr/bin/env python3
"""
Browser Automation Executor — Generates automation code for Hermes browser_exec.
"""
import json
import os
from pathlib import Path

BASE = Path(r"C:\Users\HP\AppData\Local\hermes")


def generate_automation_code(step_seq):
    """Generate browser automation code for one pin."""
    account = step_seq["account"]
    serial = step_seq["serial"]
    session = step_seq["session"]
    vault_handle = step_seq["vault_handle"]
    steps = step_seq["steps"]
    
    lines = []
    lines.append(f'session = "{session}"')
    lines.append('goto_url("https://www.pinterest.com/")')
    lines.append('wait_for_load()')
    lines.append(f'# Login with vault: {vault_handle}')
    lines.append('# browser_vault_fill(handle="{}")'.format(vault_handle))
    lines.append('wait_for_load()')
    
    for step in steps:
        action = step["action"]
        
        if action == "goto":
            lines.append('goto_url("{}")'.format(step["url"]))
            lines.append('wait_for_load()')
        
        elif action == "vault_fill":
            lines.append('# vault_fill: {}'.format(step["handle"]))
            lines.append('wait_for_load()')
        
        elif action == "upload_media":
            media_path = step["media_path"].replace("\\", "\\\\")
            basename = os.path.basename(media_path)
            media_type = step["media_type"]
            lines.append('# Upload media')
            lines.append('js("""')
            lines.append('const input = document.querySelector(\'input[type="file"]\');')
            lines.append('if (input) {')
            lines.append('    const file = new File(["{}"], "{}", {{type: "{}"}});'.format(media_path, basename, media_type))
            lines.append('    const dt = new DataTransfer();')
            lines.append('    dt.items.add(file);')
            lines.append('    input.files = dt;')
            lines.append('    input.dispatchEvent(new Event(\'change\', {bubbles: true}));')
            lines.append('}')
            lines.append('""")')
            lines.append('wait_for_load()')
        
        elif action == "fill_title":
            title = step["title"].replace('"', '\\"')
            lines.append('# Fill title')
            lines.append('js("""')
            lines.append('document.querySelector("[data-test-id=\\"pin-title-input\\"], [placeholder*=\\"Title\\"], input[placeholder*=\\"Title\\"]")?.focus();')
            lines.append('document.execCommand("insertText", false, "{}");'.format(title))
            lines.append('""")')
            lines.append('wait_for_load()')
        
        elif action == "fill_description":
            desc = step["description"].replace('"', '\\"')
            lines.append('# Fill description')
            lines.append('js("""')
            lines.append('document.querySelector("[data-test-id=\\"pin-description-input\\"], [placeholder*=\\"Description\\"], textarea[placeholder*=\\"Description\\"]")?.focus();')
            lines.append('document.execCommand("insertText", false, "{}");'.format(desc))
            lines.append('""")')
            lines.append('wait_for_load()')
        
        elif action == "select_board":
            board = step["board_name"].replace('"', '\\"')
            lines.append('# Select board')
            lines.append('js("""')
            lines.append('document.querySelector("[data-test-id=\\"board-selector\\"], button:has-text(\\"Select board\\")")?.click();')
            lines.append('""")')
            lines.append('wait_for_load()')
            lines.append('js("""')
            lines.append('document.querySelector("[role=\\"option\\"]:has-text(\\"{}\\")")?.click();'.format(board))
            lines.append('""")')
            lines.append('wait_for_load()')
        
        elif action == "fill_link":
            link = step["link"].replace('"', '\\"')
            lines.append('# Fill link')
            lines.append('js("""')
            lines.append('document.querySelector("[data-test-id=\\"pin-link-input\\"], input[placeholder*=\\"Link\\"], input[placeholder*=\\"Destination\\"]")?.focus();')
            lines.append('document.execCommand("insertText", false, "{}");'.format(link))
            lines.append('""")')
            lines.append('wait_for_load()')
        
        elif action == "publish":
            lines.append('# Publish')
            lines.append('js("""')
            lines.append('document.querySelector("[data-test-id=\\"publish-button\\"], button:has-text(\\"Publish\\"), button:has-text(\\"Save\\")")?.click();')
            lines.append('""")')
            lines.append('wait_for_load()')
            lines.append('print("  Posted successfully")')
    
    return "\n".join(lines)


def main():
    steps_file = BASE / "rboutique-affiliate" / "scripts" / "pinterest_automation_steps.json"
    if not steps_file.exists():
        print("No automation steps file found.")
        return
    
    with open(steps_file, "r") as f:
        all_steps = json.load(f)
    
    print(f"Generating automation code for {len(all_steps)} pins...")
    
    for step_seq in all_steps:
        account = step_seq["account"]
        serial = step_seq["serial"]
        session = step_seq["session"]
        
        code = generate_automation_code(step_seq)
        
        temp_file = BASE / "rboutique-affiliate" / "scripts" / f"auto_pinterest_{account}_{serial}.py"
        with open(temp_file, "w") as f:
            f.write(code)
        
        print(f"  Generated: {temp_file}")
        print(f"  Execute: browser_exec(code=open('{temp_file}').read(), session='{session}')")
    
    print("\nAll automation codes ready. Orchestrator will execute them.")


if __name__ == "__main__":
    main()