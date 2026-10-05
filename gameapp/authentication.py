import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist


class JWTAuthenticationError(Exception):
    pass


def create_token(user):
    import datetime

    now = datetime.datetime.now(datetime.timezone.utc)
    payload = {
        'sub': user.username,
        'role': user.role,
        'iat': now,
        'exp': now + datetime.timedelta(seconds=settings.APP_JWT_EXPIRATION_SECONDS),
    }
    return jwt.encode(payload, settings.APP_JWT_SECRET, algorithm='HS256')


def get_authenticated_user(request):
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        raise JWTAuthenticationError('Authentication required.')

    token = header[7:]
    try:
        payload = jwt.decode(token, settings.APP_JWT_SECRET, algorithms=['HS256'])
        username = payload.get('sub')
        if not username:
            raise JWTAuthenticationError('Invalid authentication token.')
        user = get_user_model().objects.get(username=username)
        if not user.is_active:
            raise JWTAuthenticationError('User account is inactive.')
        return user
    except (jwt.InvalidTokenError, ObjectDoesNotExist, KeyError) as exc:
        raise JWTAuthenticationError('Invalid authentication token.') from exc


def require_user(request):
    return get_authenticated_user(request)


def require_admin(request):
    user = get_authenticated_user(request)
    if user.role != get_user_model().Role.ADMIN:
        raise JWTAuthenticationError('Admin access required.')
    return user
