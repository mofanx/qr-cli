"""
QR Code Generator Module
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import qrcode


# QR Code capacity (max bytes per version with error correction)
# Format: (version, L, M, Q, H) -> max bytes
QR_CAPACITY = {
    1: (17, 14, 11, 7),
    2: (32, 26, 20, 14),
    3: (53, 42, 32, 24),
    5: (106, 84, 64, 48),
    10: (174, 136, 108, 82),
    15: (264, 208, 164, 124),
    20: (368, 288, 228, 172),
    25: (472, 368, 292, 220),
    30: (568, 444, 352, 264),
    40: (920, 716, 568, 428),
}


def get_max_chunk_size(error_correction: str = "M", max_version: int = 40) -> int:
    """
    Get maximum data capacity for a QR code.

    Args:
        error_correction: Error correction level (L, M, Q, H)
        max_version: Maximum QR version to use (1-40, default 40)

    Returns:
        Maximum bytes that can be stored
    """
    ec_index = {"L": 0, "M": 1, "Q": 2, "H": 3}[error_correction]
    return QR_CAPACITY.get(max_version, QR_CAPACITY[40])[ec_index]


def generate_qr(
    data: str,
    output: Optional[str] = None,
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
    version: Optional[int] = None,
    error_correction: str = "M",
) -> str:
    """
    Generate a QR code from text data.

    Args:
        data: Text content to encode in QR code
        output: Output file path (if None, generates timestamp-based name)
        box_size: Size of each box in pixels
        border: Border size in boxes
        fill_color: QR code color
        back_color: Background color
        version: QR code version (1-40, None for auto)
        error_correction: Error correction level (L, M, Q, H)

    Returns:
        Path to the generated QR code image
    """
    error_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }

    qr = qrcode.QRCode(
        version=version,
        error_correction=error_map.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Generate output path if not provided
    if output is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = f"qr_{timestamp}.png"

    # Ensure output directory exists
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img.save(str(output_path))
    return str(output_path)


def generate_qr_terminal(data: str) -> None:
    """
    Display a QR code in the terminal.

    Args:
        data: Text content to encode
    """
    import sys
    import io

    qr = qrcode.QRCode()
    qr.add_data(data)
    qr.make(fit=True)

    # Capture output to handle encoding properly
    buffer = io.StringIO()
    qr.print_ascii(out=buffer, invert=True)
    output = buffer.getvalue()

    # Print with proper encoding handling
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            print(output)
        except (AttributeError, OSError):
            print(output.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))
    else:
        print(output)


def generate_batch(
    data_list: list[str],
    output_dir: str,
    prefix: str = "qr",
    **kwargs,
) -> list[str]:
    """
    Generate multiple QR codes from a list of data.

    Args:
        data_list: List of text content to encode
        output_dir: Directory to save QR codes
        prefix: Filename prefix
        **kwargs: Additional arguments passed to generate_qr

    Returns:
        List of generated file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    generated_files = []

    for i, data in enumerate(data_list, 1):
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in data[:30])
        filename = output_path / f"{prefix}_{i:03d}_{safe_name}.png"

        file_path = generate_qr(data, str(filename), **kwargs)
        generated_files.append(file_path)

    return generated_files


def generate_large_text(
    data: str,
    output_dir: str,
    prefix: str = "part",
    chunk_size: Optional[int] = None,
    error_correction: str = "M",
    max_version: int = 40,
    show_progress: bool = True,
    **kwargs,
) -> list[str]:
    """
    Generate multiple QR codes from large text by chunking.

    Args:
        data: Text content to encode (can be very large)
        output_dir: Directory to save QR codes
        prefix: Filename prefix
        chunk_size: Bytes per chunk (None = auto calculate)
        error_correction: Error correction level (L, M, Q, H)
        max_version: Maximum QR version (1-40)
        show_progress: Show progress messages
        **kwargs: Additional arguments passed to generate_qr

    Returns:
        List of generated file paths
    """
    if not data:
        return []

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Auto calculate chunk size if not specified
    if chunk_size is None:
        # Reserve some space for metadata like "1/10:"
        chunk_size = get_max_chunk_size(error_correction, max_version) - 20

    # Encode data to bytes for chunking
    data_bytes = data.encode("utf-8")

    # Split into chunks
    chunks = []
    for i in range(0, len(data_bytes), chunk_size):
        chunk_bytes = data_bytes[i:i + chunk_size]
        # Use base64 or hex for safe encoding
        chunk_hex = chunk_bytes.hex()
        chunks.append(chunk_hex)

    total = len(chunks)
    generated_files = []

    if show_progress:
        print(f"Splitting {len(data_bytes)} bytes into {total} QR codes...")

    for i, chunk in enumerate(chunks, 1):
        # Format: "part/total:hex_data"
        qr_data = f"{i}/{total}:{chunk}"

        filename = output_path / f"{prefix}_{i:03d}_of_{total:03d}.png"
        file_path = generate_qr(qr_data, str(filename), error_correction=error_correction, **kwargs)
        generated_files.append(file_path)

        if show_progress:
            print(f"  [{i}/{total}] {filename.name}")

    if show_progress:
        print(f"Generated {total} QR codes in {output_dir}")

    return generated_files


def recover_large_text(qr_files: list[str], show_progress: bool = True) -> str:
    """
    Recover original text from chunked QR codes.

    Args:
        qr_files: List of QR code image files to decode
        show_progress: Show progress messages

    Returns:
        Recovered text content

    Raises:
        ValueError: If QR files are invalid or missing
    """
    try:
        from qrcode import decode_qr
    except ImportError:
        # Fallback for older qrcode versions
        from qrcode import main as qr_main
        from PIL import Image

        def decode_qr(img_path):
            img = Image.open(img_path)
            return qr_main.decode(img)

    # Sort files by name to ensure correct order
    sorted_files = sorted(qr_files, key=lambda p: Path(p).name)

    chunks = {}

    for qr_file in sorted_files:
        try:
            result = decode_qr(qr_file)
            if result and result[0].data:
                decoded = result[0].data.decode("utf-8")
            else:
                raise ValueError(f"No data found in {qr_file}")

            # Parse "part/total:hex_data"
            if ":" not in decoded:
                raise ValueError(f"Invalid QR data format in {qr_file}")

            meta, hex_data = decoded.split(":", 1)
            if "/" not in meta:
                raise ValueError(f"Invalid QR metadata in {qr_file}")

            part_num, total = meta.split("/")
            part_num = int(part_num)
            chunks[part_num] = hex_data

            if show_progress:
                print(f"  [{part_num}/{total}] Decoded {Path(qr_file).name}")

        except Exception as e:
            raise ValueError(f"Error decoding {qr_file}: {e}")

    # Reassemble in order
    if not chunks:
        raise ValueError("No valid QR data found")

    # Verify we have all chunks
    expected_parts = max(chunks.keys())
    for i in range(1, expected_parts + 1):
        if i not in chunks:
            raise ValueError(f"Missing chunk {i}")

    # Combine hex data and decode
    combined_hex = "".join(chunks[i] for i in range(1, expected_parts + 1))
    data_bytes = bytes.fromhex(combined_hex)
    return data_bytes.decode("utf-8")


def generate_qr_for_clipboard(output_dir: Optional[str] = None) -> str:
    """
    Generate QR code from clipboard text.

    Args:
        output_dir: Directory to save QR code (default: ~/qr_output)

    Returns:
        Path to generated QR code
    """
    from qr_cli.clipboard import get_clipboard_text

    data = get_clipboard_text()
    if not data:
        raise ValueError("Clipboard is empty")

    # Set default output directory
    if output_dir is None:
        home = Path.home()
        output_dir = home / "qr_output"
        output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in data[:50])
    output = output_dir / f"clipboard_{timestamp}_{safe_name}.png"

    return generate_qr(data, str(output))
