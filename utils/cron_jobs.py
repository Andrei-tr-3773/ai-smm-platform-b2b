"""
Cron jobs for periodic tasks.

This module contains scripts that should be run on a schedule using cron.

IMPORTANT: Set up cron jobs on the server with:

    # Reset monthly campaign limits on 1st of each month at midnight
    0 0 1 * * cd /path/to/project && poetry run python -c "from utils.cron_jobs import reset_monthly_limits; reset_monthly_limits()"

    # Or using absolute path:
    0 0 1 * * /usr/bin/python3 /path/to/project/utils/cron_jobs.py

For manual testing:
    python -c "from utils.cron_jobs import reset_monthly_limits; reset_monthly_limits()"
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from repositories.workspace_repository import WorkspaceRepository
from utils.mongodb_utils import get_mongo_client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def reset_monthly_limits():
    """
    Reset monthly campaign counters for all workspaces.

    This should be run on the 1st of each month via cron.

    Cron setup:
        0 0 1 * * cd /path/to/project && poetry run python -c "from utils.cron_jobs import reset_monthly_limits; reset_monthly_limits()"

    Returns:
        int: Number of workspaces reset
    """
    logger.info("Starting monthly limits reset...")

    try:
        workspace_repo = WorkspaceRepository()
        client = get_mongo_client()
        db = client.get_database("marketing_db")
        workspaces_collection = db.get_collection("workspaces")

        # Get all workspaces
        workspaces = workspaces_collection.find({})

        count = 0
        errors = 0

        for ws in workspaces:
            try:
                workspace_id = str(ws["_id"])
                workspace_repo.reset_monthly_limits(workspace_id)
                count += 1

                logger.debug(f"Reset limits for workspace: {workspace_id} (plan: {ws.get('plan_tier', 'unknown')})")

            except Exception as e:
                logger.error(f"Failed to reset workspace {ws.get('_id')}: {e}")
                errors += 1

        logger.info(f"✅ Monthly limits reset complete: {count} workspaces reset, {errors} errors")

        return count

    except Exception as e:
        logger.error(f"❌ Monthly limits reset failed: {e}")
        raise


def cleanup_expired_sessions():
    """
    Clean up expired JWT sessions (optional).

    Note: JWT tokens are stateless, so this is only needed if storing
    sessions in a database. Currently not needed.
    """
    logger.info("Session cleanup not implemented (JWT tokens are stateless)")
    pass


def send_usage_reminders():
    """
    Send email reminders to users approaching their limits (Week 7).

    This will:
    - Find workspaces at 80% of campaign limit
    - Send email reminder to upgrade
    - Find workspaces that hit limit 3+ times
    - Send personalized upgrade offer

    Coming in Week 7 with SendGrid integration.
    """
    logger.info("Usage reminders not implemented yet (coming in Week 7)")
    pass


def generate_monthly_reports():
    """
    Generate monthly usage reports for workspace owners (Week 7).

    This will:
    - Calculate total campaigns created
    - Calculate total cost (estimated)
    - Compare to previous month
    - Send via email

    Coming in Week 7 with SendGrid integration.
    """
    logger.info("Monthly reports not implemented yet (coming in Week 7)")
    pass


def verify_backups():
    """
    Verify database backups exist and are valid.

    This should be run weekly via cron (Sundays at 3 AM):
        0 3 * * 0 cd /path/to/project && poetry run python -c "from utils.cron_jobs import verify_backups; verify_backups()"

    Checks:
    - Last 7 days of backups exist
    - Backup files are not empty (> 1 MB)
    - Backup log shows no errors

    Returns:
        bool: True if all checks pass, False otherwise
    """
    import os
    from datetime import datetime, timedelta
    from pathlib import Path

    logger.info("Starting weekly backup verification...")

    backup_dir = Path.home() / "backups"

    if not backup_dir.exists():
        logger.error(f"❌ Backup directory not found: {backup_dir}")
        return False

    # Check last 7 days
    today = datetime.now()
    missing_days = []
    undersized_backups = []

    for i in range(7):
        check_date = today - timedelta(days=i)
        # Backup format: mongodb_YYYYMMDD_*.tar.gz
        date_prefix = check_date.strftime("mongodb_%Y%m%d")

        # Find backup for this day
        backups_for_day = list(backup_dir.glob(f"{date_prefix}_*.tar.gz"))

        if not backups_for_day:
            missing_days.append(check_date.strftime("%Y-%m-%d"))
            logger.warning(f"⚠️  No backup found for {check_date.strftime('%Y-%m-%d')}")
        else:
            # Check file size (should be > 1 MB)
            backup_file = backups_for_day[0]  # Take first if multiple
            size_mb = backup_file.stat().st_size / (1024 * 1024)

            if size_mb < 1:
                undersized_backups.append((check_date.strftime("%Y-%m-%d"), size_mb))
                logger.warning(f"⚠️  Backup too small for {check_date.strftime('%Y-%m-%d')}: {size_mb:.2f} MB")
            else:
                logger.debug(f"✅ Backup OK for {check_date.strftime('%Y-%m-%d')}: {size_mb:.2f} MB")

    # Check backup log for errors
    log_file = backup_dir / "backup.log"
    error_count = 0

    if log_file.exists():
        with open(log_file, 'r') as f:
            # Check last 100 lines for errors
            lines = f.readlines()[-100:]
            error_count = sum(1 for line in lines if '❌ ERROR' in line or 'ERROR' in line)

        if error_count > 0:
            logger.warning(f"⚠️  Found {error_count} errors in backup log (last 100 lines)")
    else:
        logger.warning("⚠️  Backup log not found")

    # Summary
    issues = []
    if missing_days:
        issues.append(f"{len(missing_days)} missing backups: {', '.join(missing_days)}")
    if undersized_backups:
        issues.append(f"{len(undersized_backups)} undersized backups")
    if error_count > 0:
        issues.append(f"{error_count} errors in log")

    if issues:
        logger.warning(f"⚠️  Backup verification found issues: {' | '.join(issues)}")
        # TODO: Send alert email (Week 8+)
        return False
    else:
        logger.info("✅ Backup verification passed: All 7 days present, sizes OK, no errors")
        return True


if __name__ == "__main__":
    """
    Run cron job from command line.

    Usage:
        python utils/cron_jobs.py
        python -m utils.cron_jobs
        python -c "from utils.cron_jobs import reset_monthly_limits; reset_monthly_limits()"
    """
    print("=" * 60)
    print("AI SMM Platform - Cron Jobs")
    print("=" * 60)
    print()

    print("Running monthly limits reset...")
    count = reset_monthly_limits()
    print(f"✅ Reset {count} workspaces")
    print()

    print("Cron job complete!")
