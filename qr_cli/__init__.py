"""
qr-cli - Fast QR code generator with clipboard support and batch processing
"""

__version__ = "0.1.0"

from qr_cli.generator import generate_qr, generate_qr_terminal
from qr_cli.clipboard import get_clipboard_text

__all__ = [
    "generate_qr",
    "generate_qr_terminal",
    "get_clipboard_text",
    "__version__",
]
