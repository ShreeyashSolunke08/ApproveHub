import time
from functools import wraps
from flask import request, jsonify

# Key: (endpoint, ip_or_identifier) -> list of timestamp floats
_REQUEST_HISTORY = {}

def rate_limit(limit=10, period=60, message="Too many requests. Please slow down and try again shortly."):
    """
    Lightweight, thread-safe in-memory rate limiting decorator.
    :param limit: Max requests allowed in the time window
    :param period: Time window in seconds (default 60s)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Resolve client identifier: header X-Forwarded-For or remote_addr
            forwarded = request.headers.get("X-Forwarded-For")
            client_ip = forwarded.split(",")[0].strip() if forwarded else request.remote_addr or "unknown_client"
            
            # Combine endpoint and IP
            rule_key = f"{request.endpoint}:{client_ip}"
            now = time.time()
            
            # Clean expired timestamps
            timestamps = _REQUEST_HISTORY.get(rule_key, [])
            valid_timestamps = [t for t in timestamps if now - t < period]
            
            if len(valid_timestamps) >= limit:
                retry_after = int(period - (now - valid_timestamps[0])) + 1
                response = jsonify({
                    "success": False,
                    "error": message,
                    "retry_after_seconds": max(1, retry_after)
                })
                response.status_code = 429
                response.headers["Retry-After"] = str(max(1, retry_after))
                return response
            
            valid_timestamps.append(now)
            _REQUEST_HISTORY[rule_key] = valid_timestamps
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def clear_rate_limits():
    """Testing helper to clear recorded hits."""
    _REQUEST_HISTORY.clear()
