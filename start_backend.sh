#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Virtual environment not found. Create it first:"
  echo "  python3 -m venv .venv"
  exit 1
fi

source .venv/bin/activate
export PYTHONPATH="$PWD"

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
