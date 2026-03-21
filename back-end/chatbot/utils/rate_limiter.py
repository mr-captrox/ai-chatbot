import time
from typing import List, Dict
from fastapi import HTTPException

class RateLimiter:
    """Simple in-memory rate limiter."""
    def __init__(self, limit: int = 10, period: int = 60):
        self.limit = limit
        self.period = period
        self.requests: Dict[str, List[float]] = {}

    def check(self, key: str = "global"):
        """Check if request is within limits."""
        now = time.time()
        if key not in self.requests:
            self.requests[key] = []
        
        # Filter outdated requests
        self.requests[key] = [t for t in self.requests[key] if now - t < self.period]
        
        if len(self.requests[key]) >= self.limit:
            wait_time = int(self.period - (now - self.requests[key][0]))
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Please wait {wait_time} seconds. (Max 10 req/min)"
            )
        
        self.requests[key].append(now)
        return True

    def get_status(self, key: str = "chat_limit"):
        """Get remaining requests and wait time."""
        now = time.time()
        if key not in self.requests:
            return self.limit, 0
            
        self.requests[key] = [t for t in self.requests[key] if now - t < self.period]
        remaining = self.limit - len(self.requests[key])
        wait_time = 0
        if remaining <= 0:
            wait_time = int(self.period - (now - self.requests[key][0]))
        return remaining, wait_time

# Initialize a global rate limiter
limiter = RateLimiter(limit=10, period=60)
