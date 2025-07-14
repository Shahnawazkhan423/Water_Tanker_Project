
from importlib import import_module
from django.conf import settings
from django.utils.functional import SimpleLazyObject

class MultiAppSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Decide which session to use based on path
        if request.path.startswith('/Supplier/'):
            session_key = 'supplier_sessionid'
            session_engine = settings.SUPPLIER_SESSION_ENGINE
        elif request.path.startswith('/Customer/'):
            session_key = 'customer_sessionid'
            session_engine = settings.CUSTOMER_SESSION_ENGINE
        else:
            session_key = settings.SESSION_COOKIE_NAME
            session_engine = settings.SESSION_ENGINE

        # Load correct backend engine
        engine = import_module(session_engine)
        request.session_cookie_name = session_key

        def get_session():
            session_key_val = request.COOKIES.get(session_key)
            return engine.SessionStore(session_key_val)

        request.session = SimpleLazyObject(get_session)

        response = self.get_response(request)

        # Save session and set cookie
        if request.session.modified:
            request.session.save()
            response.set_cookie(
                key=session_key,
                value=request.session.session_key,
                max_age=60 * 60 * 24,
                path='/',
                httponly=True,
                samesite='Lax',
            )

        return response
