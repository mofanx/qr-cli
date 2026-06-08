"""
Clipboard Module - Handle clipboard operations across platforms
"""
import sys


def get_clipboard_text() -> str:
    """
    Get text from clipboard.

    Returns:
        Clipboard text content, empty string if unavailable
    """
    try:
        import pyperclip
        return pyperclip.paste() or ""
    except Exception as e:
        print(f"Warning: Could not access clipboard: {e}", file=sys.stderr)
        return ""


def set_clipboard_text(text: str) -> bool:
    """
    Set text to clipboard.

    Args:
        text: Text to copy to clipboard

    Returns:
        True if successful, False otherwise
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"Warning: Could not set clipboard: {e}", file=sys.stderr)
        return False
