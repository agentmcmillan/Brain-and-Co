#!/bin/bash
# Generate mTLS certificates for Network MCP
# Creates a CA + client certificates for each device/user
set -e

CERT_DIR="$(dirname "$0")/client-certs"
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

# --- Step 1: Generate CA (Certificate Authority) ---
if [ ! -f ca.key ]; then
    echo "=== Generating Certificate Authority ==="
    openssl genrsa -out ca.key 4096
    openssl req -new -x509 -days 3650 -key ca.key -out ca.crt \
        -subj "/C=US/O=Cubic Build/CN=Network MCP CA"
    echo "CA created: ca.crt + ca.key"
else
    echo "CA already exists, skipping..."
fi

# --- Step 2: Generate client certificates ---
generate_client_cert() {
    local NAME=$1
    local CN=$2

    if [ -f "${NAME}.p12" ]; then
        echo "Client cert '${NAME}' already exists, skipping..."
        return
    fi

    echo "=== Generating client cert: ${NAME} ==="

    # Generate key
    openssl genrsa -out "${NAME}.key" 2048

    # Generate CSR
    openssl req -new -key "${NAME}.key" -out "${NAME}.csr" \
        -subj "/C=US/O=Cubic Build/CN=${CN}"

    # Sign with CA
    openssl x509 -req -days 365 -in "${NAME}.csr" \
        -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out "${NAME}.crt"

    # Create PKCS12 bundle (for easy import on devices)
    openssl pkcs12 -export -out "${NAME}.p12" \
        -inkey "${NAME}.key" -in "${NAME}.crt" -certfile ca.crt \
        -passout pass:""

    # Cleanup CSR
    rm -f "${NAME}.csr"

    echo "Created: ${NAME}.crt, ${NAME}.key, ${NAME}.p12"
}

# Generate certs for each device/user
generate_client_cert "mac-studio" "Mac Studio"
generate_client_cert "nas" "NAS Server"
generate_client_cert "proxmox" "Proxmox Host"
generate_client_cert "spark-fleet" "Spark Fleet"
generate_client_cert "conor" "Conor McMillan"

echo ""
echo "=== Certificate Generation Complete ==="
echo ""
echo "Files in ${CERT_DIR}:"
ls -la *.crt *.key *.p12 2>/dev/null
echo ""
echo "To add a new client:"
echo "  ./generate-certs.sh  # Re-run (existing certs are preserved)"
echo "  # Or manually: generate_client_cert 'device-name' 'Common Name'"
echo ""
echo "Distribute .p12 files to devices securely."
echo "For Claude Code clients, use the .crt + .key files."
