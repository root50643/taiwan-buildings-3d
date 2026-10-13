#!/bin/sh
set -eu
cd "$(dirname "$0")"
python validate_model.py
python check_layers.py
python check_contour_validity.py
python check_thin_features.py
sha256sum -c SHA256SUMS.txt
