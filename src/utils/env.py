import os

def get(key: str):
  return os.environ.get(key)