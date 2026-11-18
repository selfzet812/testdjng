#!/bin/bash
set -euo pipefail


OUT_DIR="nginx/ssl"
DAYS=365
HOST="${1:-127.0.0.1}"
mkdir -p "$OUT_DIR"

if [[ "$HOST" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  SAN="IP:$HOST,DNS:localhost"
else 
  SAN="DNS:$HOST,DNS:localhost"
fi


openssl req -x509 -nodes -days "$DAYS" -newkey rsa:2048 \
  -keyout "$OUT_DIR/selfsigned.key" \
  -out "$OUT_DIR/selfsigned.crt" \
  -subj "/CN=$HOST" \
  -addext "subjectAltName=$SAN"


chmod 644 "$OUT_DIR/selfsigned.key"


