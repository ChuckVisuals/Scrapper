from supabase import create_client, Client
from dotenv import load_dotenv
import os


def init_supabase() -> Client | None:
    """Initialize and return a Supabase client using env vars.
    Returns None when credentials are missing so callers can skip uploads.
    """
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    print(f"Supabase URL: {url}")
    print(f"Supabase Key: {'SET' if key else 'NOT SET'}")

    if not url or not key:
        print("WARNING: SUPABASE_URL or SUPABASE_KEY not set. Data will not be uploaded.")
        return None

    return create_client(url, key)
