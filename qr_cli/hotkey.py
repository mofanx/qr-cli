"""
Hotkey Module - Global shortcut key support for QR generation
"""
import os
import sys
import subprocess
from pathlib import Path


def start_hotkey_listener(
    hotkey: str = "f8+o",
    output_dir: str = None,
    show_notification: bool = True,
) -> None:
    """
    Start global hotkey listener for QR code generation.

    Args:
        hotkey: Hotkey combination (default: f8+o)
        output_dir: Directory to save QR codes
        show_notification: Show notification on QR generation

    Note:
        Requires keyboard package and administrator privileges on Windows.
    """
    try:
        import keyboard
    except ImportError:
        print("Error: keyboard package not installed. Install with: pip install keyboard")
        sys.exit(1)

    # Set default output directory
    if output_dir is None:
        output_dir = str(Path.home() / "qr_output")

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Starting hotkey listener...")
    print(f"Hotkey: {hotkey}")
    print(f"Output directory: {output_dir}")
    print(f"Press {hotkey} to generate QR from clipboard")
    print("Press Ctrl+C to exit")

    def on_hotkey():
        try:
            from qr_cli.generator import generate_qr_for_clipboard

            output_path = generate_qr_for_clipboard(output_dir=output_dir)

            msg = f"QR Code generated: {output_path}"
            print(f"\n{msg}")

            if show_notification:
                show_desktop_notification("QR Code Generated", msg)

        except Exception as e:
            error_msg = f"Failed to generate QR: {e}"
            print(f"\n{error_msg}")
            if show_notification:
                show_desktop_notification("QR Code Error", error_msg)

    # Register hotkey
    keyboard.add_hotkey(hotkey, on_hotkey)

    # Keep the script running
    keyboard.wait()


def show_desktop_notification(title: str, message: str) -> None:
    """
    Show desktop notification (platform-specific).

    Args:
        title: Notification title
        message: Notification message
    """
    try:
        if sys.platform == "win32":
            # Windows toast notification
            import win10toast
            toaster = win10toast.ToastNotifier()
            toaster.show_toast(title, message, duration=3, threaded=True)

        elif sys.platform == "darwin":
            # macOS notification
            subprocess.run([
                "osascript",
                "-e",
                f'display notification "{message}" with title "{title}"'
            ])

        elif sys.platform.startswith("linux"):
            # Linux notification (requires libnotify-bin)
            try:
                subprocess.run(
                    ["notify-send", title, message],
                    check=True,
                    stderr=subprocess.DEVNULL,
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass  # notify-send not available

    except ImportError:
        # Fallback: just print to console
        pass


def check_keyboard_permission() -> bool:
    """
    Check if we have permission to use keyboard hotkeys.

    Returns:
        True if hotkeys can be registered, False otherwise
    """
    try:
        import keyboard

        # Try to record a single event to check permissions
        # This won't actually record anything, just check if we can
        original_hook = keyboard.hook(lambda e: None)
        keyboard.unhook(original_hook)
        return True

    except (ImportError, PermissionError, keyboard.KeyboardImportError):
        return False
