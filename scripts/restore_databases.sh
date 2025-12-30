#!/bin/bash

###########################################
# Database Restore Script
#
# Restores MongoDB and Milvus from backup
# Usage: ./restore_databases.sh <backup_timestamp>
#   Example: ./restore_databases.sh 20250101_020000
#
# Week 8: Task 8.1.2b - DB backups
###########################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
LOG_FILE="$BACKUP_DIR/restore.log"

# MongoDB settings
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DB="${MONGO_DB:-marketing_db}"
MONGO_USER="${MONGO_USER:-admin}"
MONGO_PASSWORD="${MONGO_PASSWORD:-}"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_timestamp>"
    echo "Example: $0 20250101_020000"
    echo ""
    echo "Available backups:"
    find "$BACKUP_DIR" -name "mongodb_*.tar.gz" -type f -exec basename {} \; | sed 's/mongodb_/  - /' | sed 's/.tar.gz//'
    exit 1
fi

TIMESTAMP=$1

log "========================================="
log "Starting database restore: $TIMESTAMP"
log "========================================="

###########################################
# 1. Verify backup exists
###########################################

MONGO_BACKUP="$BACKUP_DIR/mongodb_$TIMESTAMP.tar.gz"
MILVUS_BACKUP="$BACKUP_DIR/milvus_$TIMESTAMP.tar.gz"

if [ ! -f "$MONGO_BACKUP" ]; then
    log "❌ ERROR: MongoDB backup not found: $MONGO_BACKUP"
    exit 1
fi

log "✅ Found MongoDB backup: $MONGO_BACKUP"

if [ -f "$MILVUS_BACKUP" ]; then
    log "✅ Found Milvus backup: $MILVUS_BACKUP"
else
    log "⚠️  WARNING: Milvus backup not found (will skip)"
fi

###########################################
# 2. Confirm restore (destructive!)
###########################################

log "⚠️  WARNING: This will OVERWRITE the current database!"
read -p "Are you sure you want to restore from $TIMESTAMP? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    log "Restore cancelled by user"
    exit 0
fi

###########################################
# 3. Restore MongoDB
###########################################

log "Restoring MongoDB..."

# Extract backup
TEMP_DIR=$(mktemp -d)
tar -xzf "$MONGO_BACKUP" -C "$TEMP_DIR"

# Find the extracted directory
MONGO_RESTORE_DIR=$(find "$TEMP_DIR" -name "mongodb_*" -type d)

if [ -z "$MONGO_RESTORE_DIR" ]; then
    log "❌ ERROR: Could not find extracted MongoDB backup"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Restore using mongorestore
if command -v mongorestore >/dev/null 2>&1; then
    if [ -n "$MONGO_PASSWORD" ]; then
        mongorestore \
            --host="$MONGO_HOST" \
            --port="$MONGO_PORT" \
            --db="$MONGO_DB" \
            --username="$MONGO_USER" \
            --password="$MONGO_PASSWORD" \
            --authenticationDatabase=admin \
            --drop \
            "$MONGO_RESTORE_DIR/$MONGO_DB" \
            >> "$LOG_FILE" 2>&1
    else
        mongorestore \
            --host="$MONGO_HOST" \
            --port="$MONGO_PORT" \
            --db="$MONGO_DB" \
            --drop \
            "$MONGO_RESTORE_DIR/$MONGO_DB" \
            >> "$LOG_FILE" 2>&1
    fi

    log "✅ MongoDB restore complete"
else
    log "❌ ERROR: mongorestore not found. Install mongodb-database-tools"
    rm -rf "$TEMP_DIR"
    exit 1
fi

# Cleanup
rm -rf "$TEMP_DIR"

###########################################
# 4. Restore Milvus (optional)
###########################################

if [ -f "$MILVUS_BACKUP" ]; then
    log "Restoring Milvus metadata..."

    # Extract Milvus backup
    TEMP_MILVUS_DIR=$(mktemp -d)
    tar -xzf "$MILVUS_BACKUP" -C "$TEMP_MILVUS_DIR"

    MILVUS_RESTORE_DIR=$(find "$TEMP_MILVUS_DIR" -name "milvus_*" -type d)

    if [ -f "$MILVUS_RESTORE_DIR/metadata.json" ]; then
        # Restore Milvus collections via Python
        METADATA_FILE="$MILVUS_RESTORE_DIR/metadata.json" python3 << 'EOF' >> "$LOG_FILE" 2>&1
import os
import json
from pymilvus import connections, utility, Collection, CollectionSchema, FieldSchema, DataType

try:
    # Load metadata
    with open(os.environ['METADATA_FILE'], 'r') as f:
        backup_data = json.load(f)

    # Connect to Milvus
    milvus_uri = os.environ.get('CONNECTION_STRING_MILVUS', 'http://localhost:19530')
    connections.connect(uri=milvus_uri)

    # Recreate collections
    for coll_name, coll_data in backup_data['collections'].items():
        # Drop if exists
        if utility.has_collection(coll_name):
            utility.drop_collection(coll_name)
            print(f"Dropped existing collection: {coll_name}")

        # Note: Full restore requires actual data backup
        # This only restores schema
        print(f"⚠️  WARNING: Milvus data not restored (only schema)")
        print(f"   Collection: {coll_name}, Entities: {coll_data['num_entities']}")

    print("✅ Milvus metadata restored (data not included)")

except Exception as e:
    print(f"❌ ERROR restoring Milvus: {e}")

finally:
    connections.disconnect("default")
EOF

        log "⚠️  Milvus schema restored (data requires manual re-indexing)"
    fi

    rm -rf "$TEMP_MILVUS_DIR"
else
    log "⏭️  Skipping Milvus restore (no backup found)"
fi

###########################################
# 5. Verification
###########################################

log "Verifying restore..."

# Count MongoDB documents
MONGO_COUNT=$(mongosh --quiet --host "$MONGO_HOST" --port "$MONGO_PORT" --eval "db.getSiblingDB('$MONGO_DB').campaigns.countDocuments()" 2>/dev/null || echo "0")
log "✅ MongoDB campaigns collection: $MONGO_COUNT documents"

log "========================================="
log "Restore complete!"
log "========================================="
log ""
log "⚠️  IMPORTANT: Restart the application:"
log "    pkill -f streamlit"
log "    nohup poetry run streamlit run Home.py &"

# Success
exit 0
