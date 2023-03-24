import os

def get_extensions():
  extensions = []
  for filename in os.listdir("./src/cogs"):
    if filename.endswith(".py"):
      extensions.append(f"cogs.{filename[:-3]}")
  return extensions