#!/bin/bash

###########################################
# Database Backup Script
#
# Backs up MongoDB and Milvus databases
# Run daily via cron: 0 2 * * * /path/to/backup_databases.sh
#
# Week 8: Task 8.1.2b - DB backups
###########################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$BACKUP_DIR/backup.log"

# MongoDB settings (from .env)
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27017}"
MONGO_DB="${MONGO_DB:-marketing_db}"
MONGO_USER="${MONGO_USER:-admin}"
MONGO_PASSWORD="${MONGO_PASSWORD:-}"

# Milvus settings
MILVUS_DATA_DIR="${MILVUS_DATA_DIR:-/var/lib/milvus}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Starting database backup: $TIMESTAMP"
log "========================================="

###########################################
# 1. MongoDB Backup
###########################################

log "Backing up MongoDB ($MONGO_DB)..."

MONGO_BACKUP_DIR="$BACKUP_DIR/mongodb_$TIMESTAMP"
mkdir -p "$MONGO_BACKUP_DIR"

if command -v mongodump >/dev/null 2>&1; then
    if [ -n "$MONGO_PASSWORD" ]; then
        mongodump \
            --host="$MONGO_HOST" \
            --port="$MONGO_PORT" \
            --db="$MONGO_DB" \
            --username="$MONGO_USER" \
            --password="$MONGO_PASSWORD" \
            --authenticationDatabase=admin \
            --out="$MONGO_BACKUP_DIR" \
            >> "$LOG_FILE" 2>&1
    else
        mongodump \
            --host="$MONGO_HOST" \
            --port="$MONGO_PORT" \
            --db="$MONGO_DB" \
            --out="$MONGO_BACKUP_DIR" \
            >> "$LOG_FILE" 2>&1
    fi

    # Compress MongoDB backup
    tar -czf "$MONGO_BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" "mongodb_$TIMESTAMP"
    rm -rf "$MONGO_BACKUP_DIR"

    MONGO_SIZE=$(du -h "$MONGO_BACKUP_DIR.tar.gz" | cut -f1)
    log "✅ MongoDB backup complete: $MONGO_SIZE ($MONGO_BACKUP_DIR.tar.gz)"
else
    log "❌ ERROR: mongodump not found. Install mongodb-database-tools"
    exit 1
fi

###########################################
# 2. Milvus Backup (optional - data files)
###########################################

log "Backing up Milvus metadata..."

# Note: Milvus 2.x recommends using backup/restore API
# For now, we backup the metadata (collections schema)
# Full data backup requires Milvus Backup tool

MILVUS_BACKUP_DIR="$BACKUP_DIR/milvus_$TIMESTAMP"
mkdir -p "$MILVUS_BACKUP_DIR"

# Save Milvus collection info via Python script
python3 << 'EOF' >> "$LOG_FILE" 2>&1
import os
import json
from pymilvus import connections, utility, Collection

try:
    # Connect to Milvus
    milvus_uri = os.environ.get('CONNECTION_STRING_MILVUS', 'http://localhost:19530')
    connections.connect(uri=milvus_uri)

    # Get all collections
    collections = utility.list_collections()

    backup_data = {
        'timestamp': os.environ.get('TIMESTAMP', ''),
        'collections': {}
    }

    for coll_name in collections:
        collection = Collection(coll_name)
        collection.load()

        backup_data['collections'][coll_name] = {
            'schema': collection.schema.to_dict(),
            'num_entities': collection.num_entities,
            'indexes': [index.to_dict() for index in collection.indexes]
        }

    # Save metadata
    backup_file = f"{os.environ.get('MILVUS_BACKUP_DIR')}/metadata.json"
    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)

    print(f"✅ Milvus metadata saved: {len(collections)} collections")

except Exception as e:
    print(f"❌ ERROR backing up Milvus: {e}")

finally:
    connections.disconnect("default")
EOF

if [ -f "$MILVUS_BACKUP_DIR/metadata.json" ]; then
    tar -czf "$MILVUS_BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" "milvus_$TIMESTAMP"
    rm -rf "$MILVUS_BACKUP_DIR"

    MILVUS_SIZE=$(du -h "$MILVUS_BACKUP_DIR.tar.gz" | cut -f1)
    log "✅ Milvus metadata backup complete: $MILVUS_SIZE"
else
    log "⚠️  WARNING: Milvus backup failed (metadata.json not created)"
fi

###########################################
# 3. Cleanup old backups
###########################################

log "Cleaning up backups older than $RETENTION_DAYS days..."

find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete 2>> "$LOG_FILE"

BACKUP_COUNT=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f | wc -l)
log "✅ Cleanup complete: $BACKUP_COUNT backups remaining"

###########################################
# 4. Backup verification
###########################################

log "Verifying backups..."

# Check MongoDB backup exists and is not empty
if [ -f "$MONGO_BACKUP_DIR.tar.gz" ] && [ -s "$MONGO_BACKUP_DIR.tar.gz" ]; then
    log "✅ MongoDB backup verified"
else
    log "❌ ERROR: MongoDB backup missing or empty!"
    exit 1
fi

# Check Milvus backup (optional)
if [ -f "$MILVUS_BACKUP_DIR.tar.gz" ] && [ -s "$MILVUS_BACKUP_DIR.tar.gz" ]; then
    log "✅ Milvus backup verified"
else
    log "⚠️  WARNING: Milvus backup missing or empty"
fi

###########################################
# 5. Upload to cloud (optional - Week 8+)
###########################################

# TODO: Upload to GCS/S3 for off-site backup
# Example: gsutil cp "$BACKUP_DIR/*.tar.gz" gs://your-backup-bucket/

log "========================================="
log "Backup complete!"
log "Location: $BACKUP_DIR"
log "========================================="

# Success
exit 0
