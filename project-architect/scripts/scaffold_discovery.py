#!/usr/bin/env python3
"""
Scaffold Generator for Product Discovery
Generates Business Requirements, User Stories, and Process Maps.
"""
import argparse
import os
from pathlib import Path

BLUEPRINT_DIR = Path("project-architect/blueprints/discovery")

def load_blueprint(template_path, replacements):
    full_path = BLUEPRINT_DIR / template_path
    if not full_path.exists():
        return f"# Discovery Template {template_path} not found."
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content

def create_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created Documentation: {path}")

def scaffold(project_name: str, context: str, output: str):
    base = Path(output) / project_name / "docs" / "discovery"
    ctx = {"PROJECT": project_name, "CONTEXT": context}

    print(f"\n📋 Starting Product Discovery for: {project_name}")

    create_file(str(base / "BUSINESS_PROCESS.md"), 
                load_blueprint("business-process.md.blueprint", ctx))
    
    create_file(str(base / "USER_STORIES.md"), 
                load_blueprint("user-stories.md.blueprint", ctx))

    print(f"\n✅ Discovery phase initiated! Documents ready for review.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--context", required=True) # Ex: "Sistema de Clinica"
    parser.add_argument("--output", default=".")
    args = parser.parse_args()
    scaffold(args.name, args.context, args.output)