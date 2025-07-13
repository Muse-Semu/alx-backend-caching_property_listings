from django.core.cache import cache
from django_redis import get_redis_connection
import logging
from .models import Property

# Configure logging
logger = logging.getLogger(__name__)

def get_all_properties():
    # Check Redis for cached queryset
    all_properties = cache.get('all_properties')
    if all_properties is None:
        # Fetch from database if not in cache
        all_properties = Property.objects.all()
        # Store in Redis for 1 hour (3600 seconds)
        cache.set('all_properties', all_properties, 3600)
    return all_properties

def get_redis_cache_metrics():
    try:
        # Connect to Redis
        redis_conn = get_redis_connection("default")
        
        # Get Redis INFO stats
        info = redis_conn.info()
        
        # Extract keyspace hits and misses
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)
        
        # Calculate hit ratio
        total_requests = keyspace_hits + keyspace_misses
        hit_ratio = keyspace_hits / total_requests if total_requests > 0 else 0.0
        
        # Log metrics
        logger.info(
            "Redis Cache Metrics: hits=%d, misses=%d, hit_ratio=%.4f",
            keyspace_hits, keyspace_misses, hit_ratio
        )
        
        # Log error if hit ratio is too low (e.g., below 0.5)
        if hit_ratio < 0.5:
            logger.error("Low cache hit ratio detected: hit_ratio=%.4f", hit_ratio)
        
        # Return metrics dictionary
        return {
            'hits': keyspace_hits,
            'misses': keyspace_misses,
            'hit_ratio': hit_ratio
        }
    except Exception as e:
        # Log error if Redis connection fails
        logger.error("Failed to retrieve Redis cache metrics: %s", str(e))
        return {
            'hits': 0,
            'misses': 0,
            'hit_ratio': 0.0
        }