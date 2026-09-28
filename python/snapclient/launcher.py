"""
Start SnapCheck locally: the backend (snapserve) then the Qt client (snapclient),
which launches the Vite server of the frontend. The backend is stopped when the client exits.
"""

import argparse
import os
import secrets
import subprocess
import sys
import time

try:
    import requests

    from snapclient.constants import DEFAULT_PORT, DEFAULT_URL
    from snapclient.__main__ import main as client_main
except ImportError as e:
    # The GUI dependencies are optional with pip (snapcheck[client] extra)
    sys.exit(f'The SnapCheck client is not installed ({e}).\nInstall it with: pip install "snapcheck[client]"')

DEFAULT_BACKEND_PORT = 8050


def wait_for_backend(process: subprocess.Popen, url: str, tries: int = 100, delay: float = 0.2):
    """Wait for the backend to answer, the frontend creates its session as soon as it is loaded."""
    for _ in range(tries):
        if process.poll() is not None:
            sys.exit("Backend failed to start")
        try:
            requests.get(f"{url}/docs")
            return
        except requests.exceptions.ConnectionError:
            time.sleep(delay)
    sys.exit("Backend didn't start in time")


def main():
    parser = argparse.ArgumentParser(description="Start the SnapCheck backend and GUI")
    parser.add_argument("--backend-port", type=int, default=DEFAULT_BACKEND_PORT, help="Port of the backend server")
    parser.add_argument("--frontend-port", type=int, default=DEFAULT_PORT, help="Port of the frontend server")
    secret = parser.add_mutually_exclusive_group()
    secret.add_argument(
        "--secret",
        type=str,
        default=os.environ.get("SNAP_SECRET"),
        help="Secret key used to sign the JWT tokens (default: $SNAP_SECRET, or a random key)",
    )
    secret.add_argument("--no-secret", action="store_true", help="Disable the secret key (default: $SNAP_SECRET, or a random key)")
    args = parser.parse_args()

    api_url = f"http://{DEFAULT_URL}:{args.backend_port}"

    # The secret is given through the environment to hide it from ps
    env = os.environ.copy()
    if not args.no_secret:
        if args.secret is None:
            args.secret = secrets.token_urlsafe(32)
        env["SNAP_SECRET"] = args.secret
    backend = subprocess.Popen(
        [sys.executable, "-m", "snapserve", "--host", DEFAULT_URL, "--port", str(args.backend_port)],
        env=env,
    )
    try:
        wait_for_backend(backend, api_url)
        client_main(["--port", str(args.frontend_port), "--api-url", api_url])
    finally:
        backend.terminate()
        backend.wait()


if __name__ == "__main__":
    main()
