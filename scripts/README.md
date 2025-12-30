# Database Backup Scripts

Automated backup and restore scripts for MongoDB and Milvus databases.

## Quick Start

### 1. Install Dependencies

```bash
# Install MongoDB tools
# Ubuntu/Debian:
sudo apt-get install mongodb-database-tools

# macOS:
brew install mongodb-database-tools

# Verify:
mongodump --version
mongorestore --version
```

### 2. Set Up Daily Backups

```bash
# Add to crontab:
crontab -e

# Daily backup at 2 AM UTC:
0 2 * * * cd /path/to/ai-smm-platform-b2b && ./scripts/backup_databases.sh

# Weekly verification at 3 AM on Sundays:
0 3 * * 0 cd /path/to/ai-smm-platform-b2b && poetry run python -c "from utils.cron_jobs import verify_backups; verify_backups()"
```

### 3. Test Manual Backup

```bash
./scripts/backup_databases.sh

# Check backup created:
ls -lh ~/backups/
# Should see: mongodb_YYYYMMDD_HHMMSS.tar.gz
```

## Scripts

### `backup_databases.sh`

**Purpose:** Creates compressed backups of MongoDB and Milvus databases.

**Usage:**
```bash
./scripts/backup_databases.sh
```

**Environment Variables** (optional):
```bash
export BACKUP_DIR="$HOME/backups"     # Backup location (default: ~/backups)
export RETENTION_DAYS=7               # Keep backups for N days (default: 7)
export MONGO_HOST="localhost"         # MongoDB host
export MONGO_PORT="27017"             # MongoDB port
export MONGO_DB="marketing_db"        # Database name
export MONGO_USER="admin"             # MongoDB user
export MONGO_PASSWORD="password"      # MongoDB password
```

**Output:**
- `~/backups/mongodb_YYYYMMDD_HHMMSS.tar.gz` - MongoDB backup (compressed)
- `~/backups/milvus_YYYYMMDD_HHMMSS.tar.gz` - Milvus metadata (compressed)
- `~/backups/backup.log` - Backup log

**Retention:**
Automatically deletes backups older than `RETENTION_DAYS` (default: 7 days).

---

### `restore_databases.sh`

**Purpose:** Restores databases from backup.

**Usage:**
```bash
# List available backups:
./scripts/restore_databases.sh

# Restore specific backup:
./scripts/restore_databases.sh 20241230_020000
```

**Steps:**
1. Stops application (prevents write conflicts)
2. Extracts backup archive
3. Runs `mongorestore --drop` (overwrites existing data)
4. Restores Milvus metadata
5. Verifies restoration
6. Prompts to restart application

**⚠️ WARNING:** This is a **destructive operation**. It will overwrite current data.

**Recovery Time:** 15-30 minutes

---

## Monitoring

### Check Backup Status

```bash
# View backup log:
tail -f ~/backups/backup.log

# Check latest backup:
ls -lht ~/backups/*.tar.gz | head -5

# Verify weekly (manual):
poetry run python -c "from utils.cron_jobs import verify_backups; verify_backups()"
```

### Backup Verification Checks

The `verify_backups()` function checks:
- ✅ Last 7 days of backups exist
- ✅ Backup files are > 1 MB (not empty)
- ✅ No errors in backup log

**Alerts** (Week 8+):
- Missing backup → Email to admin
- Undersized backup → Email alert
- Backup errors → Critical alert

---

## Disaster Recovery

**See:** `/docs/DISASTER_RECOVERY.md` for full procedures.

### Quick Recovery (Accidental Deletion)

```bash
# 1. Stop app:
pkill -f streamlit

# 2. Restore yesterday's backup:
./scripts/restore_databases.sh 20241229_020000

# 3. Restart app:
nohup poetry run streamlit run Home.py --server.port=8501 &
```

**Estimated Time:** 15-30 minutes

---

## Future Enhancements

### Week 8+ Improvements

- [ ] Upload backups to GCS/S3 (off-site storage)
- [ ] Encrypted backups (AES-256)
- [ ] Email alerts for backup failures
- [ ] Automated restore tests (monthly)
- [ ] Point-in-time recovery (1-hour RPO)

### Migration to MongoDB Atlas

**Benefits:**
- Automatic continuous backup
- Instant restore from snapshots
- No manual scripts needed
- 99.995% SLA

**Cost:** ~$57/month for M10 cluster

---

## Troubleshooting

### "mongodump: command not found"

**Fix:**
```bash
# Install MongoDB tools:
# Ubuntu: sudo apt-get install mongodb-database-tools
# macOS: brew install mongodb-database-tools
```

### "Permission denied" on backup script

**Fix:**
```bash
chmod +x scripts/backup_databases.sh
chmod +x scripts/restore_databases.sh
```

### Backup file is 0 bytes

**Cause:** MongoDB connection failed (wrong credentials or host).

**Fix:**
```bash
# Check MongoDB is running:
systemctl status mongod

# Test connection:
mongosh mongodb://localhost:27017/marketing_db

# Verify .env credentials match
```

### Restore fails with "authentication failed"

**Cause:** Wrong MongoDB credentials in environment variables.

**Fix:**
```bash
# Set correct credentials before restore:
export MONGO_USER="admin"
export MONGO_PASSWORD="your_password"
./scripts/restore_databases.sh 20241230_020000
```

---

## Support

**Technical Issues:** See `/docs/DISASTER_RECOVERY.md`

**Emergency Contact:** semeniukandrei@example.com

**Last Updated:** 2024-12-30 (Week 8)
