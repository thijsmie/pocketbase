# Logs

Application log management and monitoring.

## LogService

::: pocketbase.services.log.LogService
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Log Retrieval

```python
from pocketbase import PocketBase

pb = PocketBase('http://localhost:8090')

# First authenticate as admin
await pb.collection('_superusers').auth.with_password(
    'admin@example.com', 
    'admin_password'
)

# Get recent logs
logs = await pb.logs.get_list(page=1, per_page=50)

print(f"Total logs: {logs['totalItems']}")
for log in logs['items']:
    print(f"{log['created']}: {log['level']} - {log['message']}")
```

### Filtered Log Queries

```python
# Get error logs only
error_logs = await pb.logs.get_list(
    page=1, 
    per_page=100,
    options={
        'filter': 'level = "ERROR"',
        'sort': '-created'
    }
)

# Get logs from specific date range
from datetime import datetime, timedelta

yesterday = (datetime.now() - timedelta(days=1)).isoformat()
recent_logs = await pb.logs.get_list(
    page=1,
    per_page=200,
    options={
        'filter': f'created >= "{yesterday}"',
        'sort': '-created'
    }
)

# Get logs containing specific text
auth_logs = await pb.logs.get_list(
    page=1,
    per_page=50,
    options={
        'filter': 'message ~ "auth"',
        'sort': '-created'
    }
)
```

### Log Statistics

```python
# Get hourly log statistics
stats = await pb.logs.get_stats()

print("Hourly log activity:")
for stat in stats:
    print(f"Hour {stat['hour']}: {stat['total']} entries")

# Get stats with filtering
error_stats = await pb.logs.get_stats({
    'filter': 'level = "ERROR"'
})

print("Hourly error activity:")
for stat in error_stats:
    if stat['total'] > 0:
        print(f"Hour {stat['hour']}: {stat['total']} errors")
```

### Specific Log Entry

```python
# Get a specific log entry by ID
try:
    log_entry = await pb.logs.get_one('LOG_ENTRY_ID')
    print(f"Log level: {log_entry['level']}")
    print(f"Message: {log_entry['message']}")
    print(f"Created: {log_entry['created']}")
    if 'data' in log_entry:
        print(f"Additional data: {log_entry['data']}")
except Exception as e:
    print(f"Log entry not found: {e}")
```

## Log Monitoring Patterns

### Real-time Log Monitor

```python
import asyncio
from datetime import datetime

class LogMonitor:
    def __init__(self, pb: PocketBase):
        self.pb = pb
        self.last_check = datetime.now().isoformat()
        
    async def start_monitoring(self):
        """Monitor logs in real-time"""
        while True:
            try:
                # Get new logs since last check
                new_logs = await self.pb.logs.get_list(
                    page=1,
                    per_page=100,
                    options={
                        'filter': f'created > "{self.last_check}"',
                        'sort': 'created'
                    }
                )
                
                # Process new logs
                for log in new_logs['items']:
                    await self.process_log(log)
                    self.last_check = log['created']
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error monitoring logs: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def process_log(self, log):
        """Process individual log entries"""
        level = log['level']
        message = log['message']
        
        if level == 'ERROR':
            print(f"🚨 ERROR: {message}")
            await self.handle_error(log)
        elif level == 'WARN':
            print(f"⚠️ WARNING: {message}")
        elif level == 'INFO':
            print(f"ℹ️ INFO: {message}")
    
    async def handle_error(self, log):
        """Handle error logs - send alerts, etc."""
        # Send notification, create ticket, etc.
        print(f"Handling error log: {log['id']}")

# Usage
monitor = LogMonitor(pb)
asyncio.create_task(monitor.start_monitoring())
```

### Log Analysis

```python
async def analyze_logs():
    """Analyze logs for patterns and issues"""
    
    # Get all logs from last 24 hours
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    logs = await pb.logs.get_full_list({
        'filter': f'created >= "{yesterday}"'
    })
    
    # Analyze by level
    level_counts = {}
    for log in logs:
        level = log['level']
        level_counts[level] = level_counts.get(level, 0) + 1
    
    print("Log level distribution (last 24h):")
    for level, count in level_counts.items():
        print(f"  {level}: {count}")
    
    # Find most common error messages
    error_logs = [log for log in logs if log['level'] == 'ERROR']
    error_messages = {}
    
    for log in error_logs:
        message = log['message']
        error_messages[message] = error_messages.get(message, 0) + 1
    
    print("\nMost common errors:")
    sorted_errors = sorted(error_messages.items(), key=lambda x: x[1], reverse=True)
    for message, count in sorted_errors[:5]:
        print(f"  {count}x: {message}")
    
    return {
        'total_logs': len(logs),
        'level_distribution': level_counts,
        'top_errors': sorted_errors[:5]
    }

# Run analysis
analysis = await analyze_logs()
```

### Log Cleanup

```python
async def cleanup_old_logs():
    """Clean up old log entries (admin only)"""
    
    # Define retention period (e.g., 30 days)
    retention_date = (datetime.now() - timedelta(days=30)).isoformat()
    
    # Get old logs
    old_logs = await pb.logs.get_full_list({
        'filter': f'created < "{retention_date}"'
    })
    
    print(f"Found {len(old_logs)} old log entries to clean up")
    
    # Note: PocketBase doesn't provide a direct delete method for logs
    # This would typically be handled by PocketBase's automatic cleanup
    # or through direct database access
    
    return len(old_logs)

# Run cleanup
old_count = await cleanup_old_logs()
```

### Error Alerting System

```python
import smtplib
from email.mime.text import MIMEText

class LogAlerting:
    def __init__(self, pb: PocketBase, smtp_config: dict):
        self.pb = pb
        self.smtp_config = smtp_config
        self.error_threshold = 10  # Alert after 10 errors in 5 minutes
        self.time_window = 300  # 5 minutes
        
    async def check_error_rate(self):
        """Check if error rate exceeds threshold"""
        five_minutes_ago = (datetime.now() - timedelta(seconds=self.time_window)).isoformat()
        
        recent_errors = await self.pb.logs.get_list(
            page=1,
            per_page=1000,
            options={
                'filter': f'level = "ERROR" && created >= "{five_minutes_ago}"'
            }
        )
        
        error_count = recent_errors['totalItems']
        
        if error_count >= self.error_threshold:
            await self.send_alert(error_count)
            return True
        
        return False
    
    async def send_alert(self, error_count: int):
        """Send email alert for high error rate"""
        subject = f"PocketBase Alert: {error_count} errors in {self.time_window//60} minutes"
        body = f"""
        High error rate detected in PocketBase!
        
        Error count: {error_count}
        Time window: {self.time_window//60} minutes
        Threshold: {self.error_threshold}
        
        Please check the application logs for details.
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.smtp_config['from']
        msg['To'] = self.smtp_config['to']
        
        # Send email (implement based on your SMTP setup)
        print(f"📧 Alert sent: {subject}")

# Usage
alerting = LogAlerting(pb, {
    'from': 'alerts@yourapp.com',
    'to': 'admin@yourapp.com'
})

# Check periodically
while True:
    await alerting.check_error_rate()
    await asyncio.sleep(300)  # Check every 5 minutes
```

## Log Filtering Reference

### By Level
```python
# Error logs only
'filter': 'level = "ERROR"'

# Warning and error logs
'filter': 'level = "WARN" || level = "ERROR"'

# All except debug
'filter': 'level != "DEBUG"'
```

### By Time
```python
from datetime import datetime, timedelta

# Last hour
hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
'filter': f'created >= "{hour_ago}"'

# Specific date range
start_date = "2024-01-01T00:00:00.000Z"
end_date = "2024-01-02T00:00:00.000Z"
'filter': f'created >= "{start_date}" && created <= "{end_date}"'

# Today's logs
today = datetime.now().strftime("%Y-%m-%d")
'filter': f'created >= "{today}T00:00:00.000Z"'
```

### By Content
```python
# Authentication related logs
'filter': 'message ~ "auth"'

# Database errors
'filter': 'message ~ "database" && level = "ERROR"'

# Specific user actions
'filter': 'message ~ "user@example.com"'

# Multiple keywords
'filter': 'message ~ "login" || message ~ "signup"'
```

### Complex Filters
```python
# Critical errors in last hour
hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
'filter': f'level = "ERROR" && created >= "{hour_ago}" && message ~ "critical"'

# Non-info logs from today
today = datetime.now().strftime("%Y-%m-%d")
'filter': f'created >= "{today}T00:00:00.000Z" && level != "INFO"'
```

## Integration Examples

### FastAPI Health Endpoint

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/admin/logs/health")
async def log_health():
    """Check log health - recent error rate"""
    try:
        # Check error rate in last hour
        hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
        recent_errors = await pb.logs.get_list(
            page=1, per_page=1,
            options={'filter': f'level = "ERROR" && created >= "{hour_ago}"'}
        )
        
        error_count = recent_errors['totalItems']
        
        return {
            'status': 'healthy' if error_count < 50 else 'degraded',
            'recent_errors': error_count,
            'threshold': 50
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
log_entries_total = Counter('pocketbase_log_entries_total', 'Total log entries', ['level'])
log_processing_time = Histogram('pocketbase_log_processing_seconds', 'Log processing time')

async def export_log_metrics():
    """Export log metrics to Prometheus"""
    while True:
        try:
            # Get recent logs
            five_minutes_ago = (datetime.now() - timedelta(minutes=5)).isoformat()
            recent_logs = await pb.logs.get_full_list({
                'filter': f'created >= "{five_minutes_ago}"'
            })
            
            # Update metrics
            level_counts = {}
            for log in recent_logs:
                level = log['level']
                level_counts[level] = level_counts.get(level, 0) + 1
            
            for level, count in level_counts.items():
                log_entries_total.labels(level=level).inc(count)
            
        except Exception as e:
            print(f"Error exporting metrics: {e}")
        
        await asyncio.sleep(300)  # Update every 5 minutes

# Start Prometheus metrics server
start_http_server(8000)
asyncio.create_task(export_log_metrics())
```

## Error Handling

```python
from pocketbase import PocketBaseError

async def safe_log_query():
    try:
        logs = await pb.logs.get_list(page=1, per_page=50)
        return logs
    except PocketBaseError as e:
        if e.status == 401:
            print("Authentication required for log access")
        elif e.status == 403:
            print("Insufficient permissions for log access")
        else:
            print(f"Error fetching logs: {e}")
        return None
```
