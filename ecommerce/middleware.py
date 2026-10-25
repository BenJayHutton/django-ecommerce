import logging

logger = logging.getLogger("project_error_log")

class GlobalExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            logger.exception("Unhandled exception for %s %s", request.method, request.path)
            raise