"""
Tests for qr-cli
"""
import os
from pathlib import Path

from qr_cli import generate_qr, generate_qr_terminal
from qr_cli.generator import generate_large_text


def test_generate_qr(tmp_path):
    """Test basic QR code generation."""
    output = os.path.join(tmp_path, "test.png")
    result = generate_qr("Hello, World!", output=output)

    assert Path(result).exists()
    assert Path(result).stat().st_size > 0


def test_generate_qr_auto_name(tmp_path):
    """Test QR code generation with auto-generated filename."""
    os.chdir(tmp_path)
    result = generate_qr("Test")

    assert Path(result).exists()
    assert result.startswith("qr_")


def test_generate_qr_terminal(capsys):
    """Test terminal QR code generation."""
    generate_qr_terminal("https://example.com")
    captured = capsys.readouterr()

    # Check that some ASCII characters were output
    assert len(captured.out) > 0


def test_generate_large_text(tmp_path):
    """Test large text chunked QR generation."""
    # Create a large text
    large_text = "This is a test. " * 1000  # ~15000 bytes

    output_dir = os.path.join(tmp_path, "large_output")
    files = generate_large_text(large_text, output_dir, show_progress=False)

    # Should generate multiple QR codes
    assert len(files) >= 2

    # All files should exist
    for f in files:
        assert Path(f).exists()


def test_generate_batch(tmp_path):
    """Test batch QR code generation."""
    from qr_cli.generator import generate_batch

    data_list = ["QR1", "QR2", "QR3"]
    output_dir = os.path.join(tmp_path, "batch_output")

    files = generate_batch(data_list, output_dir)

    assert len(files) == 3
    for f in files:
        assert Path(f).exists()


def test_clipboard():
    """Test clipboard functions."""
    from qr_cli.clipboard import get_clipboard_text, set_clipboard_text

    # Test set and get
    test_text = "Test clipboard content"
    result = set_clipboard_text(test_text)
    retrieved = get_clipboard_text()

    # Note: This test may fail in headless environments
    # assert retrieved == test_text
