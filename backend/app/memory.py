# import redis
import json
# from app.config import REDIS_URL

# redis_client = redis.Redis.from_url(REDIS_URL)

# def save_memory(session_id: str, key_points: str):
#     redis_client.set(
#         f"memory:{session_id}",
#         json.dumps(key_points),
#         ex=3600  # 1 hour expiry
#     )

# def load_memory(session_id: str):
#     data = redis_client.get(f"memory:{session_id}")
#     if data:
#         return json.loads(data)
#     return ""

# In-memory session storage
# Data resets when backend restarts

memory_store = {}

def save_memory(session_id: str, key_points: str):
    """
    Save only important summarized memory.
    """
    memory_store[session_id] = key_points


def load_memory(session_id: str):
    """
    Load stored memory for session.
    """
    return memory_store.get(session_id, "")