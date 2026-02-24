from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

_url = (os.getenv("SUPABASE_URL") or "").strip().strip('"').strip("'")
_key = (os.getenv("SUPABASE_ANON_KEY") or "").strip().strip('"').strip("'")

if not _url or not _key:
    raise ValueError(
        "Missing Supabase config. In backend/.env set SUPABASE_URL and SUPABASE_ANON_KEY. "
        "Get them from your Supabase project: Project Settings → API."
    )

supabase = create_client(_url, _key)
