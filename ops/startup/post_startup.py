# ops/startup/post_startup.py
import os
import threading
import time
import tarfile
from pathlib import Path

print("🔥 POST_STARTUP FILE LOADED — SEMANTIC+CACHE VERSION")

# ---------------------------------------------------------
# Helpers (small + Cloud Run safe)
# ---------------------------------------------------------

def _download_from_gcs(gs_uri: str, dst_path: Path) -> bool:
    """
    Download a single object from GCS -> local file.
    Returns True if downloaded, False otherwise.
    """
    try:
        if not gs_uri.startswith("gs://"):
            return False

        # gs://bucket/path/to/file
        _, _, rest = gs_uri.partition("gs://")
        bucket_name, _, blob_name = rest.partition("/")
        if not bucket_name or not blob_name:
            return False

        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if not blob.exists(client):
            print(f"[POST-STARTUP][HF-CACHE] GCS object missing: {gs_uri}")
            return False

        dst_path.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(str(dst_path))
        print(f"[POST-STARTUP][HF-CACHE] Downloaded: {gs_uri} -> {dst_path}")
        return True
    except Exception as e:
        print(f"[POST-STARTUP][HF-CACHE][ERROR] download failed: {e}")
        return False


def _extract_tar_gz(src_tar: Path, dst_dir: Path) -> bool:
    try:
        dst_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(src_tar, "r:gz") as tf:
            tf.extractall(path=dst_dir)
        print(f"[POST-STARTUP][HF-CACHE] Extracted -> {dst_dir}")
        return True
    except Exception as e:
        print(f"[POST-STARTUP][HF-CACHE][ERROR] extract failed: {e}")
        return False


def _maybe_prepare_hf_offline_cache() -> bool:
    """
    If GCS cache is configured, pull it to /tmp/huggingface/hub and enable offline.
    Returns True if offline cache is ready.
    """
    gs_uri = os.getenv("NATACHA_HF_CACHE_URI", "").strip()
    if not gs_uri:
        return False

    # Use same cache dirs semantic_core expects
    hf_home = Path(os.getenv("HF_HOME", "/tmp/huggingface"))
    hub_dir = hf_home / "hub"

    # If already present, go offline immediately
    marker = hub_dir / "models--sentence-transformers--all-MiniLM-L6-v2"
    if marker.exists():
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        print("[POST-STARTUP][HF-CACHE] Cache present. Offline mode enabled.")
        return True

    # Otherwise, try to download tarball from GCS
    tar_local = Path("/tmp/hf_cache/hf_hub_miniLM.tar.gz")
    ok = _download_from_gcs(gs_uri, tar_local)
    if not ok:
        return False

    ok = _extract_tar_gz(tar_local, hub_dir)
    if not ok:
        return False

    # Enable offline mode to prevent HF API calls (avoids 429)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    print("[POST-STARTUP][HF-CACHE] Offline mode enabled (cache restored).")
    return True


def post_startup_init():
    """
    Todo lo pesado va acá.
    Cloud Run ya dio READY cuando esto corre.
    """
    print("[POST-STARTUP] Starting delayed init...")
    time.sleep(1)

    # -------------------------
    # Memory ensure (existing)
    # -------------------------
    try:
        from unified_core.memory_lazy import get_memory_engine
        mem = get_memory_engine()
        mem.ensure_loaded()
        print("[POST-STARTUP] Memory ensured")
    except Exception as e:
        print(f"[POST-STARTUP][MEMORY][ERROR] {e}")

    # -------------------------
    # Semantic core (flagged)
    # -------------------------
    if os.getenv("NATACHA_SEMANTIC_STARTUP") == "1":
        # Try to enable offline cache first (prevents HF 429)
        _maybe_prepare_hf_offline_cache()

        # Retry loop (small, avoids hammering)
        max_attempts = int(os.getenv("NATACHA_SEMANTIC_MAX_ATTEMPTS", "5"))
        base_sleep = float(os.getenv("NATACHA_SEMANTIC_RETRY_BASE_SLEEP", "2.0"))

        for attempt in range(1, max_attempts + 1):
            try:
                from unified_core.semantic_core import get_semantic_core
                core = get_semantic_core()
                core.ensure_loaded()
                print("[POST-STARTUP][SEMANTIC] Loaded successfully")
                break
            except Exception as e:
                msg = str(e)
                print(f"[POST-STARTUP][SEMANTIC][ERROR] attempt {attempt}/{max_attempts}: {msg}")

                # If rate limited, backoff harder
                sleep_s = base_sleep * (2 ** (attempt - 1))
                if "429" in msg or "Too Many Requests" in msg:
                    sleep_s = max(sleep_s, 10.0)

                if attempt == max_attempts:
                    break

                time.sleep(min(sleep_s, 60.0))

    # -------------------------
    # Auto-warmup (existing)
    # -------------------------
    try:
        from ops.startup.auto_warmup import maybe_auto_warmup
        maybe_auto_warmup()
        print("[POST-STARTUP] Auto-warmup done")
    except Exception as e:
        print(f"[POST-STARTUP][WARMUP][ERROR] {e}")


def launch_post_startup():
    t = threading.Thread(
        target=post_startup_init,
        daemon=True
    )
    t.start()
