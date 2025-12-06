import time
import os
from typing import Dict, Optional

# In-memory store for circuit state
# Format: { "provider_name": { "failures": int, "last_failure": float, "is_open": bool } }
_CIRCUIT_STATE: Dict[str, Dict] = {}

def _get_ttl() -> int:
    return int(os.getenv("CIRCUIT_TTL_SECONDS", "600"))

def mark_failure(name: str):
    """Record a failure for a provider and potentially open the circuit."""
    now = time.time()
    if name not in _CIRCUIT_STATE:
        _CIRCUIT_STATE[name] = {"failures": 0, "last_failure": 0, "is_open": False}
    
    state = _CIRCUIT_STATE[name]
    state["failures"] += 1
    state["last_failure"] = now
    
    # Simple logic: 1 critical failure (like quota) or 3 consecutive errors opens circuit
    # For now, we treat any explicit mark_failure as critical enough to consider opening
    # But let's stick to the user requirement: "circuit breaker that temporarily disables a failing provider"
    # We'll open it immediately on mark_failure for simplicity as requested for RateLimits
    state["is_open"] = True
    print(f"🔌 Circuit breaker OPENED for {name} (TTL: {_get_ttl()}s)")

def is_open(name: str) -> bool:
    """Check if the circuit is open (provider disabled)."""
    if name not in _CIRCUIT_STATE:
        return False
    
    state = _CIRCUIT_STATE[name]
    if not state["is_open"]:
        return False
    
    # Check if TTL expired
    now = time.time()
    ttl = _get_ttl()
    if now - state["last_failure"] > ttl:
        # Half-open / Reset
        print(f"🔌 Circuit breaker RESET for {name} (TTL expired)")
        state["is_open"] = False
        state["failures"] = 0
        return False
        
    return True

def clear_failure(name: str):
    """Reset failure count for a provider."""
    if name in _CIRCUIT_STATE:
        _CIRCUIT_STATE[name] = {"failures": 0, "last_failure": 0, "is_open": False}
