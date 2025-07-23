# Backups

Database backup management for PocketBase.

## BackupService

::: pocketbase.services.backup.BackupService
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Listing Backups

```python
from pocketbase import PocketBase

pb = PocketBase('http://localhost:8090')

# First authenticate as admin
await pb.collection('_superusers').auth.with_password(
    'admin@example.com', 
    'admin_password'
)

# Get all available backups
backups = await pb.backups.get_full_list()

print(f"Available backups: {len(backups)}")
for backup in backups:
    print(f"- {backup['key']} ({backup['size']} bytes, modified: {backup['modified']})")
```

### Creating Backups

```python
# Create a backup with auto-generated name
await pb.backups.create()
print("Backup created successfully")

# Create a backup with custom name
backup_name = f"manual_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
await pb.backups.create(backup_name)
print(f"Backup created: {backup_name}")
```

### Downloading Backups

```python
# Download a specific backup
backup_name = "backup_20240101_120000.zip"
backup_data = await pb.backups.download(backup_name)

# Save to local file
with open(f"local_{backup_name}", 'wb') as f:
    f.write(backup_data)

print(f"Backup downloaded: {len(backup_data)} bytes")
```

### Uploading Backups

```python
# Upload a backup file
with open('external_backup.zip', 'rb') as f:
    await pb.backups.upload(('external_backup.zip', f, 'application/zip'))

print("Backup uploaded successfully")
```

### Restoring from Backup

```python
# Restore from a specific backup
backup_name = "backup_20240101_120000.zip"
await pb.backups.restore(backup_name)
print(f"Database restored from {backup_name}")

# Note: This will restart the PocketBase server
# Your application should handle reconnection
```

### Deleting Backups

```python
# Delete a specific backup
backup_name = "old_backup_20231201_120000.zip"
await pb.backups.delete(backup_name)
print(f"Backup deleted: {backup_name}")
```

## Backup Management Patterns

### Automated Backup Scheduler

```python
import asyncio
from datetime import datetime, timedelta

class BackupScheduler:
    def __init__(self, pb: PocketBase):
        self.pb = pb
        self.backup_interval = 24 * 60 * 60  # 24 hours
        self.max_backups = 7  # Keep 7 days of backups
        
    async def start_scheduling(self):
        """Start automatic backup scheduling"""
        while True:
            try:
                await self.create_scheduled_backup()
                await self.cleanup_old_backups()
                
                # Wait for next backup
                await asyncio.sleep(self.backup_interval)
                
            except Exception as e:
                print(f"Backup scheduling error: {e}")
                # Wait 1 hour before retry on error
                await asyncio.sleep(3600)
    
    async def create_scheduled_backup(self):
        """Create a scheduled backup with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"auto_backup_{timestamp}.zip"
        
        try:
            await self.pb.backups.create(backup_name)
            print(f"✅ Scheduled backup created: {backup_name}")
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            raise
    
    async def cleanup_old_backups(self):
        """Remove old automatic backups"""
        try:
            backups = await self.pb.backups.get_full_list()
            
            # Filter automatic backups and sort by modification date
            auto_backups = [
                b for b in backups 
                if b['key'].startswith('auto_backup_')
            ]
            auto_backups.sort(key=lambda x: x['modified'], reverse=True)
            
            # Delete old backups beyond the limit
            if len(auto_backups) > self.max_backups:
                old_backups = auto_backups[self.max_backups:]
                for backup in old_backups:
                    await self.pb.backups.delete(backup['key'])
                    print(f"🗑️ Deleted old backup: {backup['key']}")
                    
        except Exception as e:
            print(f"Error during backup cleanup: {e}")

# Usage
scheduler = BackupScheduler(pb)
asyncio.create_task(scheduler.start_scheduling())
```

### Backup Verification

```python
async def verify_backup(backup_name: str) -> bool:
    """Verify that a backup exists and is valid"""
    try:
        backups = await pb.backups.get_full_list()
        backup = next((b for b in backups if b['key'] == backup_name), None)
        
        if not backup:
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        # Check backup size
        if backup['size'] < 1024:  # Less than 1KB is probably invalid
            print(f"⚠️ Backup appears too small: {backup['size']} bytes")
            return False
        
        # Try to download a portion to verify it's accessible
        try:
            backup_data = await pb.backups.download(backup_name)
            if len(backup_data) != backup['size']:
                print(f"⚠️ Downloaded size mismatch: {len(backup_data)} vs {backup['size']}")
                return False
            
            print(f"✅ Backup verified: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Backup download failed: {e}")
            return False
            
    except Exception as e:
        print(f"Error verifying backup: {e}")
        return False

# Verify all backups
backups = await pb.backups.get_full_list()
for backup in backups:
    await verify_backup(backup['key'])
```

### Backup Mirroring

```python
import aiofiles
import aiohttp
from pathlib import Path

class BackupMirror:
    def __init__(self, pb: PocketBase, mirror_path: str):
        self.pb = pb
        self.mirror_path = Path(mirror_path)
        self.mirror_path.mkdir(exist_ok=True)
        
    async def sync_backups(self):
        """Sync backups to local mirror"""
        try:
            # Get remote backups
            remote_backups = await self.pb.backups.get_full_list()
            
            # Get local backups
            local_backups = set(f.name for f in self.mirror_path.glob('*.zip'))
            
            # Download missing backups
            for backup in remote_backups:
                backup_name = backup['key']
                local_path = self.mirror_path / backup_name
                
                if backup_name not in local_backups:
                    print(f"📥 Downloading {backup_name}...")
                    backup_data = await self.pb.backups.download(backup_name)
                    
                    async with aiofiles.open(local_path, 'wb') as f:
                        await f.write(backup_data)
                    
                    print(f"✅ Downloaded {backup_name} ({len(backup_data)} bytes)")
            
            # Remove local backups that don't exist remotely
            remote_backup_names = {b['key'] for b in remote_backups}
            for local_backup in local_backups:
                if local_backup not in remote_backup_names:
                    local_path = self.mirror_path / local_backup
                    local_path.unlink()
                    print(f"🗑️ Removed obsolete local backup: {local_backup}")
                    
        except Exception as e:
            print(f"Error syncing backups: {e}")
    
    async def upload_local_backup(self, local_backup_path: str):
        """Upload a local backup to PocketBase"""
        local_path = Path(local_backup_path)
        
        if not local_path.exists():
            raise FileNotFoundError(f"Local backup not found: {local_path}")
        
        async with aiofiles.open(local_path, 'rb') as f:
            content = await f.read()
            await self.pb.backups.upload((local_path.name, content, 'application/zip'))
        
        print(f"📤 Uploaded {local_path.name}")

# Usage
mirror = BackupMirror(pb, '/path/to/backup/mirror')
await mirror.sync_backups()
```

### Disaster Recovery

```python
class DisasterRecovery:
    def __init__(self, pb: PocketBase):
        self.pb = pb
        
    async def create_emergency_backup(self) -> str:
        """Create an emergency backup before risky operations"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"emergency_backup_{timestamp}.zip"
        
        try:
            await self.pb.backups.create(backup_name)
            print(f"🚨 Emergency backup created: {backup_name}")
            return backup_name
        except Exception as e:
            print(f"❌ Failed to create emergency backup: {e}")
            raise
    
    async def restore_from_latest(self):
        """Restore from the most recent backup"""
        try:
            backups = await self.pb.backups.get_full_list()
            if not backups:
                raise Exception("No backups available for restore")
            
            # Sort by modification date (most recent first)
            backups.sort(key=lambda x: x['modified'], reverse=True)
            latest_backup = backups[0]
            
            print(f"🔄 Restoring from: {latest_backup['key']}")
            await self.pb.backups.restore(latest_backup['key'])
            print("✅ Restore completed")
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            raise
    
    async def list_restore_points(self) -> list:
        """List available restore points with details"""
        backups = await self.pb.backups.get_full_list()
        backups.sort(key=lambda x: x['modified'], reverse=True)
        
        restore_points = []
        for backup in backups:
            restore_points.append({
                'name': backup['key'],
                'size': backup['size'],
                'created': backup['modified'],
                'age_hours': (
                    datetime.now() - 
                    datetime.fromisoformat(backup['modified'].replace('Z', '+00:00'))
                ).total_seconds() / 3600
            })
        
        return restore_points

# Usage
dr = DisasterRecovery(pb)

# Before risky operation
emergency_backup = await dr.create_emergency_backup()

try:
    # Perform risky operation
    await risky_database_operation()
except Exception as e:
    print(f"Operation failed: {e}")
    # Restore from emergency backup
    await pb.backups.restore(emergency_backup)
```

## Backup Best Practices

### 1. Regular Automated Backups

```python
# Schedule daily backups at 2 AM
async def schedule_daily_backup():
    while True:
        now = datetime.now()
        next_run = now.replace(hour=2, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)
        
        wait_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        # Create backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        await pb.backups.create(f"daily_backup_{timestamp}.zip")
```

### 2. Backup Rotation Policy

```python
async def implement_backup_rotation():
    """Implement 3-2-1 backup strategy"""
    backups = await pb.backups.get_full_list()
    
    # Keep: 7 daily, 4 weekly, 12 monthly
    daily_backups = []
    weekly_backups = []
    monthly_backups = []
    
    for backup in backups:
        created = datetime.fromisoformat(backup['modified'].replace('Z', '+00:00'))
        age_days = (datetime.now() - created).days
        
        if age_days <= 7:
            daily_backups.append(backup)
        elif age_days <= 28 and created.weekday() == 6:  # Sundays
            weekly_backups.append(backup)
        elif created.day == 1:  # First of month
            monthly_backups.append(backup)
    
    # Keep only the required number
    keep_backups = set()
    keep_backups.update(b['key'] for b in daily_backups[-7:])
    keep_backups.update(b['key'] for b in weekly_backups[-4:])
    keep_backups.update(b['key'] for b in monthly_backups[-12:])
    
    # Delete others
    for backup in backups:
        if backup['key'] not in keep_backups:
            await pb.backups.delete(backup['key'])
```

### 3. Backup Monitoring

```python
async def monitor_backup_health():
    """Monitor backup system health"""
    try:
        backups = await pb.backups.get_full_list()
        
        if not backups:
            print("🚨 ALERT: No backups found!")
            return False
        
        # Check latest backup age
        latest_backup = max(backups, key=lambda x: x['modified'])
        latest_time = datetime.fromisoformat(latest_backup['modified'].replace('Z', '+00:00'))
        hours_since_latest = (datetime.now() - latest_time).total_seconds() / 3600
        
        if hours_since_latest > 25:  # More than 25 hours
            print(f"⚠️ WARNING: Latest backup is {hours_since_latest:.1f} hours old")
            return False
        
        # Check backup sizes
        avg_size = sum(b['size'] for b in backups[-5:]) / min(len(backups), 5)
        for backup in backups[-3:]:  # Check last 3 backups
            if backup['size'] < avg_size * 0.5:  # Less than 50% of average
                print(f"⚠️ WARNING: Backup {backup['key']} seems unusually small")
                return False
        
        print(f"✅ Backup system healthy: {len(backups)} backups, latest {hours_since_latest:.1f}h ago")
        return True
        
    except Exception as e:
        print(f"❌ Error checking backup health: {e}")
        return False
```

## Error Handling

```python
from pocketbase import PocketBaseError

async def safe_backup_operation():
    try:
        # Create backup
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        await pb.backups.create(backup_name)
        
        # Verify it was created
        backups = await pb.backups.get_full_list()
        if not any(b['key'] == backup_name for b in backups):
            raise Exception("Backup creation verification failed")
        
        return backup_name
        
    except PocketBaseError as e:
        if e.status == 401:
            print("Authentication required for backup operations")
        elif e.status == 403:
            print("Insufficient permissions for backup operations")
        elif e.status == 507:
            print("Insufficient storage space for backup")
        else:
            print(f"Backup error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected backup error: {e}")
        return None
```
