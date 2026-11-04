import os

def validate_pdf_file(file_storage, max_bytes=10 * 1024 * 1024):
    """
    Validates uploaded file:
    1. Checks filename extension (.pdf)
    2. Validates PDF magic bytes (%PDF-) to reject disguised binaries/scripts.
    3. Verifies file size does not exceed max_bytes.
    """
    if not file_storage or not file_storage.filename:
        return False, "No file selected."

    filename = file_storage.filename.lower()
    if not filename.endswith(".pdf"):
        return False, "Invalid file format. Only official PDF documents are accepted."

    # Read first 1024 bytes to check magic header and size
    header = file_storage.read(1024)
    file_storage.seek(0, os.SEEK_END)
    file_size = file_storage.tell()
    file_storage.seek(0)  # Reset cursor for subsequent save

    if file_size > max_bytes:
        return False, f"File size exceeds limit ({max_bytes / (1024 * 1024):.0f} MB)."

    if not header.startswith(b"%PDF-"):
        return False, "File is corrupted or not a valid PDF document (magic bytes mismatch)."

    return True, "Valid PDF file."
