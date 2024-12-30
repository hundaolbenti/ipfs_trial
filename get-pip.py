import os.path
import pkgutil
import shutil
import sys
import struct
import tempfile

# Taken from: https://bootstrap.pypa.io/get-pip.py
# Simplified version for installing pip

from urllib.request import urlopen
url = "https://bootstrap.pypa.io/get-pip.py"
with urlopen(url) as response:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        shutil.copyfileobj(response, tmp_file)
