# -*- coding: utf-8 -*-
"""
Created on November 2024

@author: Ghimciuc Ioan
"""

import subprocess

venv_path = r"C:\Users\user\PycharmProjects\LowerLimbToolkit\.venv2\Scripts\python.exe"
script_path = r"C:\Users\user\PycharmProjects\LowerLimbToolkit\src\main.py"
project_dir = r"C:\Users\user\PycharmProjects\LowerLimbToolkit"

subprocess.run([venv_path, script_path], cwd=project_dir)

