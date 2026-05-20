from lepton.app import DEFAULT_HOST, DEFAULT_PORT
from snapserve import app
import argparse



parser = argparse.ArgumentParser(description="Run the SnapServe server")
parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="The host to bind the server to")
parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="The port to bind the server to")
parser.add_argument("--secret", type=str, default=None, help="Set the secret key for token generation (optional)")
parser.add_argument("--session", type=str, default=None, help="Initialize the first session with this id")
args = parser.parse_args()

if args.secret is not None:
    app.auth.secret = args.secret
if args.session is not None:
    app.store.new_session(sess_id=args.session)

app.start_uvicorn(host=args.host, port=args.port)
