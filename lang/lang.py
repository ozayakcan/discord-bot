import os
from pathlib import Path
import json

lang_code = os.environ.get("LANGUAGE_CODE")
lang_code_default = "en"
if lang_code is None:
  lang_code = lang_code_default
lang_file = "./lang/"+lang_code+".json"
path = Path(lang_file)

if not path.is_file():
  lang_file = "./lang/"+lang_code_default+".json"
  
file = open(lang_file)
lang = json.load(file)
file.close()