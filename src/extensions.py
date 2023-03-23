import os

def get_extensions():
  extensions = []
  for filename in os.listdir("./src/commands"):
    if filename.endswith(".py"):
      extensions.append(f"commands.{filename[:-3]}")
  return extensions