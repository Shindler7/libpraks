import sys

import os

INTERP = os.path.expanduser("/var/www/u0988708/data/www/coralboat.online/venv/bin/python")
if sys.executable != INTERP:
   os.execl(INTERP, INTERP, *sys.argv)

sys.path.append(os.getcwd())

from app import application