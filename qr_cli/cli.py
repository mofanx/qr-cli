"""
CLI Module - Command line interface for qr-cli
"""
import sys
from pathlib import Path

import click

from qr_cli.generator import (
    generate_qr,
    generate_qr_terminal,
    generate_batch,
    generate_qr_for_clipboard,
    generate_large_text,
)
from qr_cli.clipboard import get_clipboard_text


@click.command()
@click.version_option(version="0.1.0", prog_name="qr")
@click.option("--text", "-t", help="Text to encode in QR code")
@click.option("--clipboard", "-c", is_flag=True, help="Use text from clipboard (default)")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read text from file")
@click.option("--lines", "-l", is_flag=True, help="Line mode: each line = one QR (for URL lists)")
@click.option("--hex", "-H", is_flag=True, help="Use hex encoding (for binary data/recovery)")
@click.option("--label", "-L", is_flag=True, help="Add [序号/总数] label to content")
@click.option("--chunk-size", help="Chunk size in bytes/chars (default: auto)")
@click.option("--output", "-o", help="Output file path")
@click.option("--output-dir", "-d", help="Output directory for multi-QR mode")
@click.option("--terminal", "-T", is_flag=True, help="Display QR code in terminal")
@click.option("--hotkey", "-h", is_flag=True, help="Start hotkey listener mode (F8+O)")
@click.option("--hotkey-code", help="Custom hotkey combination (e.g., 'f9+o')")
@click.option("--box-size", default=10, help="QR code box size (default: 10)")
@click.option("--border", default=4, help="QR code border size (default: 4)")
@click.option("--error-correction", default="M", type=click.Choice(["L", "M", "Q", "H"]),
              help="Error correction level (default: M)")
def main(text, clipboard, file, lines, hex, label, chunk_size, output, output_dir, terminal, hotkey,
         hotkey_code, box_size, border, error_correction):
    """
    qr - Fast QR code generator with clipboard support.

    \b
    Quick Examples:
        qr                    # Clipboard -> qr_TIMESTAMP.png
        qr -t "Hello"         # Text -> qr_TIMESTAMP.png
        qr -t "URL" -o out.png

    \b
    File Processing:
        qr -f code.py -d ./qr           # Plain text chunks
        qr -f code.py -d ./qr -L       # With labels: [1/3]text
        qr -f code.py -d ./qr -H       # Hex encoding only
        qr -f code.py -d ./qr -H -L    # Hex with labels: 1/3:hex
        qr -f urls.txt -l -d ./qr      # Each line -> one QR

    \b
    Terminal Display:
        qr -t "text" -T       # Show QR in terminal
        qr -c -T              # Show clipboard QR in terminal

    \b
    Hotkey Mode:
        qr -h                 # Start hotkey listener (F8+O)
    """

    # Hotkey mode
    if hotkey:
        try:
            from qr_cli.hotkey import start_hotkey_listener, check_keyboard_permission

            if not check_keyboard_permission():
                click.echo("Error: Keyboard hotkeys require administrator/root privileges.", err=True)
                click.echo("On Windows: Run as Administrator", err=True)
                click.echo("On macOS/Linux: Run with sudo", err=True)
                sys.exit(1)

            start_hotkey_listener(hotkey=hotkey_code or "f8+o", output_dir=output_dir)

        except ImportError:
            click.echo("Error: Hotkey mode requires 'keyboard' package.", err=True)
            click.echo("Install with: pip install keyboard", err=True)
            sys.exit(1)
        except KeyboardInterrupt:
            click.echo("\nHotkey listener stopped.")
            sys.exit(0)
        return

    # Terminal mode
    if terminal:
        data = _get_data(text, clipboard, file, default_to_clipboard=True)
        if not data:
            click.echo("Error: No data provided", err=True)
            sys.exit(1)
        generate_qr_terminal(data)
        return

    # Multi-QR mode (file with output_dir)
    if file and output_dir:
        data = Path(file).read_text(encoding="utf-8")

        if lines:
            # Line mode: each line = one QR
            data_list = [line.strip() for line in data.splitlines() if line.strip()]
            if not data_list:
                click.echo("Error: No data found in file", err=True)
                sys.exit(1)

            click.echo(f"Generating {len(data_list)} QR codes (one per line)...")
            files = generate_batch(
                data_list,
                output_dir,
                box_size=box_size,
                border=border,
                error_correction=error_correction,
            )
            for f in files:
                click.echo(f"  [OK] {f}")
            click.echo(f"\nGenerated {len(files)} QR codes.")

        else:
            # Chunk mode: large text -> auto chunked QRs
            chunk = int(chunk_size) if chunk_size else None
            generate_large_text(
                data,
                output_dir,
                chunk_size=chunk,
                use_hex=hex,
                add_label=label,
                error_correction=error_correction,
                box_size=box_size,
                border=border,
            )

        return

    # Normal mode: get data and generate single QR
    data = _get_data(text, clipboard, file, default_to_clipboard=True)
    if not data:
        click.echo("Error: No data provided. Use -t, -c, or -f", err=True)
        sys.exit(1)

    output_path = generate_qr(
        data,
        output=output,
        box_size=box_size,
        border=border,
        error_correction=error_correction,
    )

    click.echo(f"QR: {output_path}")


def _get_data(text: str, clipboard: bool, file: str, default_to_clipboard: bool = False) -> str:
    """Get data from the first available source."""
    if text:
        return text

    if file:
        return Path(file).read_text(encoding="utf-8")

    if clipboard:
        return get_clipboard_text()

    if default_to_clipboard:
        return get_clipboard_text()

    return ""


if __name__ == "__main__":
    main()
