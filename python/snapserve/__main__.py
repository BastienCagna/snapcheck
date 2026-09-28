import argparse
import os

from lepton.app import DEFAULT_HOST, DEFAULT_PORT
from snapserve.app import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the SnapServe server")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="The host to bind the server to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="The port to bind the server to")
    parser.add_argument(
        "--secret",
        type=str,
        default=os.environ.get("SNAP_SECRET"),
        help="Secret key used to sign the JWT tokens (default: $SNAP_SECRET, or a random key)",
    )
    args = parser.parse_args()

    if args.secret:
        app.auth.secret = args.secret

    app.start_uvicorn(host=args.host, port=args.port)
