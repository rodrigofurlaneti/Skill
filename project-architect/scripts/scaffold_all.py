#!/usr/bin/env python3
"""
Master Orchestrator — Full Project Scaffold
Runs all scaffold generators in the correct order to produce a complete
.NET + React fullstack project with DDD, Clean Architecture, and SRE best practices.

Usage:
    python scripts/scaffold_all.py --name MyApp --output ./output --db sqlserver --entities Task Project
    python scripts/scaffold_all.py --name MyApp --output ./output --full
"""

import argparse
import sys
from pathlib import Path

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).resolve().parent

# Import all scaffold modules
sys.path.insert(0, str(SCRIPTS_DIR))
import scaffold_backend
import scaffold_frontend
import scaffold_auth
import scaffold_dba
import scaffold_review
import scaffold_devops
import scaffold_ux


def scaffold_full(
    name: str,
    output: str,
    db: str = "sqlserver",
    entities: list[str] = None,
    features: list[str] = None,
    multitenant: bool = True,
    theme: str = "dark",
):
    if entities is None:
        entities = ["Task", "Project"]
    if features is None:
        features = ["dashboard", "tasks"]

    print("=" * 60)
    print(f"  PROJECT ARCHITECT — Full Stack Scaffold")
    print(f"  Project: {name}")
    print(f"  Database: {db} | Multi-tenant: {'Yes' if multitenant else 'No'}")
    print(f"  Entities: {', '.join(entities)}")
    print(f"  Frontend Features: {', '.join(features)}")
    print("=" * 60)

    # 1. Backend (Clean Architecture + DDD)
    print("\n[1/7] Backend...")
    scaffold_backend.scaffold(name, output, db, entities)

    # 2. Database (Fluent API + Performance)
    print("\n[2/7] Database & Persistence...")
    scaffold_dba.scaffold(name, output, db, multitenant, entities)

    # 3. Security (JWT + Identity)
    print("\n[3/7] Security & Identity...")
    scaffold_auth.scaffold(name, output)

    # 4. Frontend (React + TypeScript + Glassmorphism)
    print("\n[4/7] Frontend...")
    scaffold_frontend.scaffold(name, output, features)

    # 5. UX/UI Design System
    print("\n[5/7] UX/UI Design System...")
    scaffold_ux.scaffold(name, output, theme)

    # 6. Code Review & Governance
    print("\n[6/7] Code Review & Governance...")
    scaffold_review.scaffold(name, output)

    # 7. DevOps (Docker + CI/CD)
    print("\n[7/7] DevOps & Observability...")
    scaffold_devops.scaffold(name, output)

    print("\n" + "=" * 60)
    print(f"  ✅ FULL SCAFFOLD COMPLETE — {name}")
    print("=" * 60)
    print(f"\n  📁 Output: {Path(output).resolve() / name}")
    print(f"\n  Next Steps:")
    print(f"  1. cd {output}/{name}")
    print(f"  2. dotnet restore && dotnet build")
    print(f"  3. cd ../{name}-frontend && npm install && npm run dev")
    print(f"  4. dotnet test (validate architecture boundaries)")
    print(f"  5. docker build -t {name.lower()} .")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Master Orchestrator — Full Project Scaffold",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full scaffold with defaults
  python scripts/scaffold_all.py --name MyApp --output ./output

  # Custom entities and PostgreSQL
  python scripts/scaffold_all.py --name ClinicVet --output ./output --db postgresql --entities Pet Owner Appointment

  # With custom frontend features
  python scripts/scaffold_all.py --name TaskFlow --output ./output --features dashboard tasks projects settings
        """,
    )
    parser.add_argument("--name", required=True, help="Project name (PascalCase)")
    parser.add_argument("--output", default=".", help="Output root directory")
    parser.add_argument(
        "--db",
        default="sqlserver",
        choices=["sqlserver", "postgresql"],
        help="Database provider",
    )
    parser.add_argument(
        "--entities",
        nargs="+",
        default=["Task", "Project"],
        help="Domain entity names",
    )
    parser.add_argument(
        "--features",
        nargs="+",
        default=["dashboard", "tasks"],
        help="Frontend feature/page names",
    )
    parser.add_argument(
        "--multitenant",
        action="store_true",
        default=True,
        help="Enable multi-tenant isolation",
    )
    parser.add_argument(
        "--theme",
        default="dark",
        choices=["dark", "light"],
        help="UI theme",
    )

    args = parser.parse_args()

    scaffold_full(
        name=args.name,
        output=args.output,
        db=args.db,
        entities=args.entities,
        features=args.features,
        multitenant=args.multitenant,
        theme=args.theme,
    )
