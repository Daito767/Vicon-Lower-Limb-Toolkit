# -*- coding: utf-8 -*-
"""
Created on November 2024

@author: Ghimciuc Ioan
"""

import subprocess
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
venv_path = os.path.join(current_dir, ".venv", "Scripts", "python.exe")
script_path = os.path.join(current_dir, "src", "main.py")

subprocess.run([venv_path, script_path], cwd=current_dir)