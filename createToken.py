from datetime import datetime, timedelta
import jwt
import uuid
from decouple    import config

SECRET_KEY = config('secretKey')
JWT_EXPIRE_HOURS = 72

access_token_exp = datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS)
access_token = jwt.encode(
    {
        'user_id': 1,
        'exp': access_token_exp,
        'type': 'access',
        'jti': str(uuid.uuid4())
    },
    SECRET_KEY,
    algorithm='HS256'
)
print(access_token)
