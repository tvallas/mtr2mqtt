"""
Workaround module for fixing test paths
"""

import os
import sys
import mtr2mqtt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../mtr2mqtt')))
