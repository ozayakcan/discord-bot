import os

__all__ = (
    'getenv',
)

def getenv(key: str):
  return os.environ.get(key)