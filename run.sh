#!/usr/bin/env bash
# NOVA-X launcher for macOS and Linux

set -e

echo ""
echo "   ========================================"
echo "   NOVA-X: Next-Gen Omniscient VAssistant X"
echo "   ========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed."
    echo "Please install Python 3.10+ from https://python.org"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create virtual environment if missing
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt

# Launch
echo "Starting NOVA-X..."
echo ""
python3 nova_x.py "$@"
