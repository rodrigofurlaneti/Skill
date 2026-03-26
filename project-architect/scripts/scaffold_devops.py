#!/usr/bin/env python3
"""
Scaffold Generator for DevOps & Observability
Generates Dockerfiles, GitHub Actions, and Serilog configurations.
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
    github = base / ".github" / "workflows"
    
    print(f"\n🚀 Scaffolding {name} DevOps & Observability (SRE Mode)")

    # ========== Dockerfile (Multi-stage & Alpine for Security) ==========
    # Nota: O Dockerfile assume que será executado na raiz da Solution
    create_file(str(base / "Dockerfile"), f"""
FROM mcr.microsoft.com/dotnet/aspnet:9.0-alpine AS base
USER app
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:9.0-alpine AS build
ARG BUILD_CONFIGURATION=Release
WORKDIR /src
COPY ["src/{name}.API/{name}.API.csproj", "src/{name}.API/"]
COPY ["src/{name}.Application/{name}.Application.csproj", "src/{name}.Application/"]
COPY ["src/{name}.Infrastructure/{name}.Infrastructure.csproj", "src/{name}.Infrastructure/"]
COPY ["src/{name}.Domain/{name}.Domain.csproj", "src/{name}.Domain/"]
RUN dotnet restore "src/{name}.API/{name}.API.csproj"
COPY . .
WORKDIR "/src/src/{name}.API"
RUN dotnet build "{name}.API.csproj" -c $BUILD_CONFIGURATION -o /app/build

FROM build AS publish
ARG BUILD_CONFIGURATION=Release
RUN dotnet publish "{name}.API.csproj" -c $BUILD_CONFIGURATION -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "{name}.API.dll"]
""")

    # ========== GitHub Actions (CI - Build & Test) ==========
    create_file(str(github / "dotnet-ci.yml"), f"""
name: .NET CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: 9.0.x
          
      - name: Restore dependencies
        run: dotnet restore
        
      - name: Build
        run: dotnet build --no-restore --configuration Release
        
      - name: Test
        run: dotnet test --no-build --verbosity normal --configuration Release
""")

    print(f"\n✅ DevOps scaffold complete!")
    print(f"   Next steps:")
    print(f"   1. Ensure all projects are under the 'src/' folder for Docker context.")
    print(f"   2. Add your GitHub Secrets if you plan to deploy to Azure/AWS.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold DevOps for .NET")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()
    scaffold(args.name, args.output)