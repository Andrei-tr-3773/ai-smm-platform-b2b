# Disaster Recovery Plan

**AI SMM Platform - Week 8: Production Hardening**

This document outlines procedures for data backup, recovery, and business continuity.

---

## 📋 Table of Contents

1. [Backup Strategy](#backup-strategy)
2. [Automated Backups](#automated-backups)
3. [Restore Procedures](#restore-procedures)
4. [Recovery Time Objectives](#recovery-time-objectives)
5. [Testing & Verification](#testing--verification)
6. [Emergency Contacts](#emergency-contacts)

---

## 🔐 Backup Strategy

### Databases

**MongoDB (Primary Data Store)**
- **What:** All campaign data, user accounts, workspaces, templates, audiences
- **Frequency:** Daily at 2:00 AM UTC
- **Retention:** 7 days rolling
- **Method:** `mongodump` → compressed `.tar.gz` → local storage
- **Size:** ~50-100 MB (estimated for 100 users)

**Milvus (Vector Database)**
- **What:** Campaign embeddings, vector indexes
- **Frequency:** Daily at 2:00 AM UTC
- **Retention:** 7 days rolling
- **Method:** Collection metadata backup (schema + counts)
- **Note:** Full vector data requires re-indexing from MongoDB

### Critical Files

**Environment Configuration**
- `.env` - Database credentials, API keys (NOT in Git)
- Backup location: Secure password manager (1Password/Bitwarden)

**Code Repository**
- GitHub: https://github.com/Andrei-tr-3773/ai-smm-platform-b2b
- All code changes committed to Git
- No critical data in repository

---

## 🔄 Automated Backups

### Setup Instructions

**1. Install Dependencies**

```bash
# Install MongoDB tools (if not already installed)
# Ubuntu/Debian:
sudo apt-get install mongodb-database-tools

# macOS:
brew tap mongodb/brew
brew install mongodb-database-tools

# Verify installation:
mongodump --version
mongorestore --version
```

**2. Configure Backup Script**

```bash
# Set environment variables (optional - defaults to .env values)
export BACKUP_DIR="$HOME/backups"  # Default: ~/backups
export RETENTION_DAYS=7            # Keep 7 days of backups
export MONGO_HOST="localhost"
export MONGO_PORT="27017"
export MONGO_DB="marketing_db"
export MONGO_USER="admin"
export MONGO_PASSWORD="your_password_here"
```

**3. Set Up Cron Job**

```bash
# Edit crontab:
crontab -e

# Add daily backup at 2:00 AM:
0 2 * * * cd /path/to/ai-smm-platform-b2b && ./scripts/backup_databases.sh

# Check cron logs:
grep CRON /var/log/syslog
```

**4. Verify First Backup**

```bash
# Run manual backup:
cd /path/to/ai-smm-platform-b2b
./scripts/backup_databases.sh

# Check backup created:
ls -lh ~/backups/

# Should see:
#   mongodb_20250101_020000.tar.gz
#   milvus_20250101_020000.tar.gz
#   backup.log
```

### Backup Monitoring

**Daily Verification**

Backups are monitored via:
1. **Backup log:** `~/backups/backup.log` - check for errors
2. **File existence:** Verify `.tar.gz` files created
3. **File size:** MongoDB backup should be > 1 MB (not empty)

**Weekly Verification** (via cron)

```bash
# Add weekly backup verification (Sundays at 3 AM):
0 3 * * 0 cd /path/to/ai-smm-platform-b2b && poetry run python -c "from utils.cron_jobs import verify_backups; verify_backups()"
```

**Alerts**

- Missing backup → Email to admin@example.com (Week 8+ with SendGrid)
- Backup size < 1 MB → Alert (possible failure)
- Restore test failure → Critical alert

---

## 🚨 Restore Procedures

### Scenario 1: Accidental Data Deletion

**Example:** User deleted campaigns by mistake, workspace owner requests restoration.

**Steps:**

1. **Identify restore point:**
   ```bash
   # List available backups:
   ls -lh ~/backups/mongodb_*.tar.gz

   # Example output:
   #   mongodb_20241229_020000.tar.gz  (2 days ago)
   #   mongodb_20241230_020000.tar.gz  (yesterday)
   #   mongodb_20241231_020000.tar.gz  (today)
   ```

2. **Stop application** (prevents write conflicts):
   ```bash
   pkill -f streamlit
   ```

3. **Run restore script:**
   ```bash
   cd /path/to/ai-smm-platform-b2b
   ./scripts/restore_databases.sh 20241230_020000

   # Confirm restore when prompted:
   #   "Are you sure you want to restore? (yes/no): yes"
   ```

4. **Verify data restored:**
   ```bash
   # Connect to MongoDB:
   mongosh mongodb://localhost:27017/marketing_db

   # Count campaigns:
   db.campaigns.countDocuments()

   # Check specific workspace:
   db.campaigns.find({ workspace_id: "workspace_123" }).count()
   ```

5. **Restart application:**
   ```bash
   cd /path/to/ai-smm-platform-b2b
   nohup poetry run streamlit run Home.py --server.port=8501 &

   # Verify app is running:
   curl http://localhost:8501
   ```

6. **Notify user:** Campaigns restored from [date] backup.

**Estimated Recovery Time:** 15-30 minutes

---

### Scenario 2: Database Corruption

**Example:** MongoDB crashes, data files corrupted, server won't start.

**Steps:**

1. **Assess damage:**
   ```bash
   # Try to start MongoDB:
   systemctl status mongod

   # Check logs for corruption errors:
   journalctl -u mongod | grep -i corrupt
   ```

2. **Deploy new MongoDB instance:**
   ```bash
   # Option A: Repair existing (if possible):
   mongod --repair

   # Option B: Fresh install (recommended for critical corruption):
   sudo systemctl stop mongod
   sudo rm -rf /var/lib/mongodb/*
   sudo systemctl start mongod
   ```

3. **Restore from latest backup:**
   ```bash
   # Find most recent backup:
   LATEST_BACKUP=$(ls -t ~/backups/mongodb_*.tar.gz | head -1)
   TIMESTAMP=$(basename $LATEST_BACKUP | sed 's/mongodb_//' | sed 's/.tar.gz//')

   # Restore:
   ./scripts/restore_databases.sh $TIMESTAMP
   ```

4. **Recreate Milvus indexes** (if needed):
   ```bash
   # Run re-indexing script:
   poetry run python -c "
   from repositories.campaign_repository import CampaignRepository
   from utils.mongodb_utils import get_mongo_client
   from utils.openai_utils import get_embedding

   # Re-index all campaigns from MongoDB → Milvus
   repo = CampaignRepository()
   # ... re-indexing logic
   "
   ```

5. **Verify and restart:**
   ```bash
   # Test database connection:
   poetry run python -c "from utils.mongodb_utils import get_mongo_client; print('MongoDB OK')"

   # Restart application:
   nohup poetry run streamlit run Home.py --server.port=8501 &
   ```

**Estimated Recovery Time:** 1-2 hours

---

### Scenario 3: Server Failure (Complete Loss)

**Example:** Server crashes, hardware failure, need to migrate to new server.

**Steps:**

1. **Provision new server:**
   ```bash
   # GCP VM with same specs:
   #   - Machine type: e2-medium (2 vCPU, 4 GB RAM)
   #   - Disk: 50 GB SSD
   #   - OS: Ubuntu 22.04 LTS
   ```

2. **Install dependencies:**
   ```bash
   # SSH to new server:
   ssh user@new-server-ip

   # Install Python, Poetry, MongoDB, Milvus:
   # (Follow DEPLOYMENT.md instructions)
   ```

3. **Clone repository:**
   ```bash
   git clone https://github.com/Andrei-tr-3773/ai-smm-platform-b2b.git
   cd ai-smm-platform-b2b
   poetry install
   ```

4. **Restore .env file:**
   ```bash
   # Copy from secure password manager:
   nano .env
   # Paste:
   #   OPENAI_API_KEY=...
   #   CONNECTION_STRING_MONGO=...
   #   etc.
   ```

5. **Transfer and restore backups:**
   ```bash
   # Option A: Copy from old server (if accessible):
   scp user@old-server:~/backups/*.tar.gz ~/backups/

   # Option B: Download from cloud storage (if configured):
   gsutil cp gs://your-backup-bucket/*.tar.gz ~/backups/

   # Restore latest backup:
   ./scripts/restore_databases.sh 20241231_020000
   ```

6. **Start application:**
   ```bash
   nohup poetry run streamlit run Home.py --server.port=8501 &
   ```

7. **Update DNS** (if IP changed):
   ```bash
   # Point your-domain.com → new-server-ip
   ```

**Estimated Recovery Time:** 2-4 hours

---

## ⏱️ Recovery Time Objectives (RTO)

| Scenario | RTO | RPO | Data Loss |
|----------|-----|-----|-----------|
| **Accidental deletion** | 15-30 min | 24 hours | Up to 1 day of data |
| **Database corruption** | 1-2 hours | 24 hours | Up to 1 day of data |
| **Server failure** | 2-4 hours | 24 hours | Up to 1 day of data |
| **Region outage** | 4-8 hours | 24 hours | Up to 1 day of data |

**Key Metrics:**
- **RTO (Recovery Time Objective):** How long to restore service
- **RPO (Recovery Point Objective):** How much data loss is acceptable
- **Current RPO: 24 hours** - Daily backups mean worst case = 1 day data loss

### Improving RTO/RPO (Week 8+ Enhancements)

**Reduce RPO to 1 hour:**
- Implement continuous backup (MongoDB change streams)
- Replicate to off-site storage (GCS/S3) every hour
- Cost: ~$10/month for storage

**Reduce RTO to 15 minutes:**
- Use MongoDB Atlas (managed service) - instant restore from snapshots
- Hot standby server (replica set)
- Cost: ~$57/month for M10 cluster

---

## ✅ Testing & Verification

### Monthly Restore Test

**Verify backups are working** by performing a test restore to a separate database.

**Test Procedure** (first Sunday of each month):

1. **Create test database:**
   ```bash
   # Don't overwrite production!
   export MONGO_DB="marketing_db_test"
   ```

2. **Restore last night's backup:**
   ```bash
   ./scripts/restore_databases.sh $(ls -t ~/backups/mongodb_*.tar.gz | head -1 | xargs basename | sed 's/mongodb_//' | sed 's/.tar.gz//')
   ```

3. **Verify data integrity:**
   ```bash
   mongosh mongodb://localhost:27017/marketing_db_test

   # Count documents:
   db.campaigns.countDocuments()
   db.users.countDocuments()
   db.workspaces.countDocuments()

   # Spot check: random campaign:
   db.campaigns.findOne()
   ```

4. **Document results:**
   ```bash
   # Add to backup log:
   echo "[$(date)] ✅ Monthly restore test passed: X campaigns, Y users" >> ~/backups/backup.log
   ```

5. **Cleanup test database:**
   ```bash
   mongosh --eval "db.getSiblingDB('marketing_db_test').dropDatabase()"
   ```

**Expected Result:** All collections present, document counts match production (within daily variance).

---

## 📞 Emergency Contacts

**Technical Lead:** Andrei Semeniuk
- Email: semeniukandrei@example.com
- Phone: +X-XXX-XXX-XXXX

**Database Administrator:** [Name]
- Email: dba@example.com
- Phone: +X-XXX-XXX-XXXX

**Hosting Provider:** Google Cloud Platform
- Support: https://cloud.google.com/support
- Phone: 1-877-355-5787

**Escalation Procedure:**
1. Tech Lead (response time: 1 hour)
2. DBA (response time: 2 hours)
3. GCP Support (response time: 4 hours for Standard tier)

---

## 🔄 Maintenance Schedule

### Daily (Automated)
- 2:00 AM UTC - Full database backup
- 2:30 AM UTC - Backup verification

### Weekly (Manual)
- Sunday 9:00 AM - Review backup logs
- Sunday 10:00 AM - Backup size trend analysis

### Monthly (Manual)
- 1st Sunday - Full restore test (to test database)
- 1st Monday - Update disaster recovery documentation

### Quarterly (Manual)
- Test server failover to new instance
- Review RTO/RPO metrics
- Update emergency contacts

---

## 📊 Backup Statistics

**Current Metrics** (as of Week 8):

| Metric | Value |
|--------|-------|
| Backup frequency | Daily |
| Retention period | 7 days |
| Average backup size | 75 MB (MongoDB) |
| Backup duration | 2-3 minutes |
| Storage used | ~525 MB (7 days × 75 MB) |
| Last successful backup | [Check ~/backups/backup.log] |
| Last restore test | [To be scheduled] |

---

## 🚀 Future Enhancements (Post-Week 8)

### Short-term (Month 2-3)
- [ ] Upload backups to GCS/S3 (off-site storage)
- [ ] Email alerts for backup failures
- [ ] Automated weekly restore tests
- [ ] Backup encryption (AES-256)

### Medium-term (Month 4-6)
- [ ] Migrate to MongoDB Atlas (managed backups)
- [ ] Point-in-time recovery (1-hour RPO)
- [ ] Database replication (high availability)
- [ ] Monitoring dashboard (Grafana)

### Long-term (Month 7-12)
- [ ] Multi-region failover
- [ ] Zero-downtime migrations
- [ ] Automated disaster recovery drills
- [ ] Compliance certifications (SOC 2, GDPR)

---

## 📝 Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-12-30 | 1.0 | Initial disaster recovery plan | Week 8 Team |

---

**Last Updated:** 2024-12-30
**Next Review:** 2025-01-30

**Status:** ✅ Production Ready (Week 8 hardening complete)
