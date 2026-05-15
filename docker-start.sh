#!/usr/bin/env bash
# ============================================================
# NutriLens AI — Docker startup helper
# ============================================================
# Usage:
#   ./docker-start.sh          # Build and start all services
#   ./docker-start.sh --down   # Stop and remove containers
#   ./docker-start.sh --logs   # Follow container logs
# ============================================================

set -euo pipefail

if [ ! -f ".env" ]; then
  echo "⚠  .env file not found — copying from .env.example"
  cp .env.example .env
  echo "📝  Please edit .env and set a strong SECRET_KEY before continuing."
  echo "    Generate one with:  python -c \"import secrets; print(secrets.token_hex(32))\""
  exit 1
fi

case "${1:-start}" in
  --down)
    echo "🛑  Stopping NutriLens AI containers..."
    docker compose down
    ;;
  --logs)
    docker compose logs -f
    ;;
  *)
    echo "🚀  Building and starting NutriLens AI..."
    docker compose up --build -d
    echo ""
    echo "✅  Services started:"
    echo "    Frontend  →  http://localhost:3000"
    echo "    Backend   →  http://localhost:8000"
    echo "    API Docs  →  http://localhost:8000/docs"
    echo ""
    echo "💡  Run './docker-start.sh --logs' to follow logs"
    ;;
esac
