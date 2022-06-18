import os
import pathlib

from tree_sitter import Language

langs = [path for path in pathlib.Path(os.getcwd()).glob("languages/*") if path.is_dir()]

for lang in langs:
    print(f"including {lang} in language library")

Language.build_library('build/languages.so', langs)
