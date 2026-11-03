"""Print version fields, or write a PyInstaller Windows version-info file."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from guess_a_sketch import version as v  # noqa: E402

if len(sys.argv) > 1 and sys.argv[1] == "--winfile":
    a, b, c = (int(x) for x in v.VERSION.split("."))
    tmpl = """VSVersionInfo(
  ffi=FixedFileInfo(filevers=({a}, {b}, {c}, 0), prodvers=({a}, {b}, {c}, 0), mask=0x3f, flags=0x0,
                    OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Shouku Games'),
      StringStruct('FileDescription', '{name} - a drawing spelling game'),
      StringStruct('FileVersion', '{ver}'),
      StringStruct('InternalName', 'GuessASketch'),
      StringStruct('LegalCopyright', 'Copyright (C) 2026 {authors}. GPL-3.0'),
      StringStruct('OriginalFilename', 'GuessASketch-{ver}-win64.exe'),
      StringStruct('ProductName', '{name}'),
      StringStruct('ProductVersion', '{ver}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    with open(sys.argv[2], "w") as f:
        f.write(tmpl.format(a=a, b=b, c=c, ver=v.VERSION, name=v.APP_NAME, authors=v.AUTHORS))
else:
    print(v.VERSION)
