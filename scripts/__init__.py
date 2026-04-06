"""Runtime compatibility helpers for the scripts package."""

import os


os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")
