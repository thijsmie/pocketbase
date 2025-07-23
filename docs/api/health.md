# Health

Health monitoring for your PocketBase instance.

## HealthService

::: pocketbase.services.health.HealthService
    options:
      show_root_heading: true
      show_source: false

## Usage Examples

### Basic Health Check

```python
from pocketbase import PocketBase

pb = PocketBase('http://localhost:8090')

# Check health status
health = await pb.health.check()

print(f"Status: {health['status']}")
print(f"Message: {health['message']}")

# Typical response:
# {
#     "status": "ok",
#     "message": "PocketBase is running"
# }
```

### Health Monitoring

```python
import asyncio
from datetime import datetime

async def monitor_health():
    """Continuously monitor PocketBase health"""
    while True:
        try:
            health = await pb.health.check()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if health['status'] == 'ok':
                print(f"✅ {timestamp}: PocketBase is healthy")
            else:
                print(f"⚠️ {timestamp}: PocketBase status: {health['status']}")
                
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"❌ {timestamp}: Health check failed: {e}")
        
        # Check every 30 seconds
        await asyncio.sleep(30)

# Run health monitoring
asyncio.create_task(monitor_health())
```

### Service Availability Check

```python
async def is_service_available() -> bool:
    """Check if PocketBase service is available"""
    try:
        health = await pb.health.check()
        return health['status'] == 'ok'
    except Exception:
        return False

# Use in your application
if await is_service_available():
    print("PocketBase is available, proceeding with operations")
    # Your application logic here
else:
    print("PocketBase is not available, using fallback")
    # Fallback logic here
```

## Integration Patterns

### Application Startup

```python
async def startup_checks():
    """Perform health checks during application startup"""
    print("🚀 Starting application...")
    
    # Check PocketBase health
    try:
        health = await pb.health.check()
        if health['status'] != 'ok':
            raise Exception(f"PocketBase unhealthy: {health}")
        print("✅ PocketBase health check passed")
    except Exception as e:
        print(f"❌ PocketBase health check failed: {e}")
        raise
    
    # Additional startup checks...
    print("🎉 Application started successfully")

# Use in your app initialization
await startup_checks()
```

### Circuit Breaker Pattern

```python
from datetime import datetime, timedelta

class PocketBaseCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            # Try health check first if in HALF_OPEN state
            if self.state == "HALF_OPEN":
                health = await pb.health.check()
                if health['status'] != 'ok':
                    raise Exception("Health check failed")
            
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
            self.failure_count = 0
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

# Usage
circuit_breaker = PocketBaseCircuitBreaker()

async def safe_database_operation():
    return await circuit_breaker.call(
        pb.collection('posts').get_full_list
    )
```

### Load Balancer Health Check

```python
from aiohttp import web

async def health_endpoint(request):
    """Health endpoint for load balancers"""
    try:
        # Check PocketBase health
        health = await pb.health.check()
        
        if health['status'] == 'ok':
            return web.json_response({
                'status': 'healthy',
                'pocketbase': health,
                'timestamp': datetime.now().isoformat()
            }, status=200)
        else:
            return web.json_response({
                'status': 'unhealthy',
                'pocketbase': health,
                'timestamp': datetime.now().isoformat()
            }, status=503)
            
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=503)

# Add to your web application
app = web.Application()
app.router.add_get('/health', health_endpoint)
```

## Error Handling

```python
from pocketbase import PocketBaseError

async def robust_health_check():
    try:
        health = await pb.health.check()
        return {
            'available': True,
            'status': health['status'],
            'message': health.get('message', 'OK')
        }
    except PocketBaseError as e:
        return {
            'available': False,
            'error': f"PocketBase error: {e}",
            'status_code': e.status
        }
    except Exception as e:
        return {
            'available': False,
            'error': f"Connection error: {e}",
            'status_code': None
        }

# Usage
health_info = await robust_health_check()
if health_info['available']:
    print("✅ Service is available")
else:
    print(f"❌ Service unavailable: {health_info['error']}")
```
