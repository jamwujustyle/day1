from redis import Redis


redis = Redis.from_url("redis://localhost:6379/0", decode_responses=True)


def get_user_lock(user_id: str, timeout: int = 300, blocking_timeout: int = 60):
    lock_key = f"user_processing_lock{user_id}"

    return redis.lock(lock_key, timeout=timeout, blocking_timeout=blocking_timeout)
