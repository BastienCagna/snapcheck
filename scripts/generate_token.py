from lepton.auth import TokenData
from snapserve import app
import sys


app.auth.secret = sys.argv[1]
sess = app.store.new_session()
dt = TokenData(sid=sess.id)
print(sess.id)
print(app.auth.create_access_token(dt))