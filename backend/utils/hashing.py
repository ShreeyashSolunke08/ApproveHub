import hashlib

def sha256_file(path):
    """
    Computes deterministic SHA-256 hash of a file by reading in 8KB chunks.
    Ensures low memory usage even for 10MB PDFs.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_file(path, stored_hash):
    """
    Checks if current file on disk matches expected cryptographic fingerprint.
    Returns True if intact, False if tampered with.
    """
    if not stored_hash:
        return False
    try:
        return sha256_file(path) == stored_hash
    except Exception:
        return False

def sha256_bytes(data: bytes):
    return hashlib.sha256(data).hexdigest()

def generate_record_hash(doc_id, step_order, approver_id, approval_no, timestamp_iso):
    """
    Generates an immutable audit fingerprint combining all approval metadata.
    """
    payload = f"{doc_id}:{step_order}:{approver_id}:{approval_no}:{timestamp_iso}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
