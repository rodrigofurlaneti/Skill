#!/usr/bin/env python3
"""
Scaffold Generator for Identity & Security
Configures JWT, Identity, and Auth Controllers.
"""
import argparse
import os
from pathlib import Path

def create_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created: {path}")

def scaffold(name: str, output: str):
    base = Path(output) / name
    app = base / "src" / f"{name}.Application"
    api = base / "src" / f"{name}.API"

    print(f"\n🔐 Scaffolding {name} Security & Identity")

    # ========== Auth Controller Base ==========
    create_file(str(api / "Controllers" / "AuthController.cs"), f"""
using Microsoft.AspNetCore.Mvc;
using {name}.Application.Features.Auth;

namespace {name}.API.Controllers;

public class AuthController : ApiController
{{
    [HttpPost("login")]
    [SkipAuthorize] // Atributo para permitir acesso anônimo
    public async Task<IActionResult> Login([FromBody] LoginCommand command)
    {{
        var result = await Mediator.Send(command);
        return Problem(result);
    }}
}}
""")

    # ========== JWT Service Logic ==========
    create_file(str(app / "Common" / "Security" / "JwtProvider.cs"), f"""
namespace {name}.Application.Common.Security;

public class JwtProvider 
{{
    // Lógica para gerar tokens com claims de TenantId e Role
}}
""")

    print(f"\n✅ Security scaffold complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--output", default=".")
    args = parser.parse_args()
    scaffold(args.name, args.output)