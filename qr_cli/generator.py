"""
QR Code Generator Module
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import qrcode


# QR Code capacity (max characters per version with error correction)
# Approximate character counts for different versions
QR_CHAR_CAPACITY = {
    1: 17, 5: 106, 10: 174, 15: 264, 20: 368, 25: 472, 30: 568, 40: 920
}


def get_max_chunk_size(error_correction: str = "M", max_version: int = 40) -> int:
    """
    Get maximum character capacity for a QR code.

    Args:
        error_correction: Error correction level (L, M, Q, H)
        max_version: Maximum QR version to use (1-40, default 40)

    Returns:
        Maximum characters that can be stored (approximate, for UTF-8 text)
    """
    # Base capacity for version 40
    base_capacity = QR_CHAR_CAPACITY.get(max_version, 920)

    # Adjust for error correction (M is baseline)
    ec_factor = {"L": 1.15, "M": 1.0, "Q": 0.85, "H": 0.7}.get(error_correction, 1.0)

    return int(base_capacity * ec_factor)


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
    use_hex: bool = False,
    add_label: bool = False,
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
        chunk_size: Characters/bytes per chunk (None = auto calculate)
        use_hex: Use hex encoding instead of plain text
        add_label: Add [序号/总数] label to content
        error_correction: Error correction level (L, M, Q, H)
        max_version: Maximum QR version (1-40)
        show_progress: Show progress messages
        **kwargs: Additional arguments passed to generate_qr

    Returns:
        List of generated file paths

    Examples:
        # Plain text (default)
        generate_large_text(text, output_dir)

        # Text with labels: "[1/3]content"
        generate_large_text(text, output_dir, add_label=True)

        # Hex only: "646566..."
        generate_large_text(text, output_dir, use_hex=True)

        # Hex with labels: "1/3:646566..."
        generate_large_text(text, output_dir, use_hex=True, add_label=True)
    """
    if not data:
        return []

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert to bytes if using hex
    if use_hex:
        raw_data = data.encode("utf-8")
        data_unit = "bytes"
    else:
        raw_data = data
        data_unit = "characters"

    # Auto calculate chunk size if not specified
    if chunk_size is None:
        max_capacity = get_max_chunk_size(error_correction, max_version)
        # Reserve space for potential label
        if add_label:
            # "[999/999]" = 11 chars, or "999/999:" = 8 chars for hex
            label_reserve = 8 if use_hex else 11
            chunk_size = max_capacity - label_reserve
        else:
            chunk_size = max_capacity

    generated_files = []

    # Split into chunks
    chunks = []
    for i in range(0, len(raw_data), chunk_size):
        chunks.append(raw_data[i:i + chunk_size])

    total = len(chunks)

    if show_progress:
        print(f"Splitting {len(raw_data)} {data_unit} into {total} QR codes...")

    for i, chunk in enumerate(chunks, 1):
        # Encode chunk based on mode
        if use_hex:
            # Bytes to hex string
            chunk_content = chunk.hex() if isinstance(chunk, bytes) else chunk
        else:
            # Keep as text
            chunk_content = chunk

        # Add label if requested
        if add_label:
            if use_hex:
                qr_data = f"{i}/{total}:{chunk_content}"
            else:
                qr_data = f"[{i}/{total}]{chunk_content}"
        else:
            qr_data = chunk_content

        filename = output_path / f"{prefix}_{i:03d}_of_{total:03d}.png"
        file_path = generate_qr(qr_data, str(filename), error_correction=error_correction, **kwargs)
        generated_files.append(file_path)

        if show_progress:
            print(f"  [{i}/{total}] {filename.name}")

    if show_progress:
        print(f"Generated {total} QR codes in {output_dir}")

        # Show what the content looks like
        if add_label:
            if use_hex:
                print(f"Format: 1/total:hex_data")
            else:
                print(f"Format: [part/total]text_content")
        else:
            if use_hex:
                print(f"Format: hex_data (no labels)")
            else:
                print(f"Format: plain_text (no labels)")

    return generated_files


def recover_large_text(qr_files: list[str], use_hex: bool = False, show_progress: bool = True) -> str:
    """
    Recover original text from chunked QR codes.

    Args:
        qr_files: List of QR code image files to decode
        use_hex: Whether the data is hex-encoded
        show_progress: Show progress messages

    Returns:
        Recovered text content

    Raises:
        ValueError: If QR files are invalid or missing

    Note:
        Requires a QR decoding library. This is a reference implementation
        showing the logic for recovering data from chunked QR codes.
    """
    # This is a reference implementation showing the recovery logic
    # Actual QR decoding requires external libraries (zxing, pyzbar, etc.)

    chunks = {}

    for i, qr_file in enumerate(qr_files, 1):
        # In real implementation, decode QR code here
        # decoded = decode_qr_code(qr_file)
        decoded = f"[{i}/{len(qr_files)}]sample_content"  # Placeholder

        # Parse based on format
        if decoded.startswith("[") and "]" in decoded:
            # Format: [1/3]content
            meta_end = decoded.index("]")
            meta = decoded[1:meta_end]
            content = decoded[meta_end + 1:]

            if "/" in meta:
                part_num = int(meta.split("/")[0])
                chunks[part_num] = content

        elif ":" in decoded and decoded.count("/") == 1:
            # Format: 1/3:hex_content
            meta, content = decoded.split(":", 1)
            if "/" in meta:
                part_num = int(meta.split("/")[0])
                chunks[part_num] = content

        else:
            # No label, use file order
            chunks[i] = decoded

    # Reassemble
    sorted_keys = sorted(chunks.keys())
    recovered = "".join(chunks[k] for k in sorted_keys)

    # Decode hex if needed
    if use_hex and recovered:
        recovered = bytes.fromhex(recovered).decode("utf-8")

    return recovered


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
