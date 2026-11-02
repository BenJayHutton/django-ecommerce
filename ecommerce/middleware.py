import logging

project_debug_log = logging.getLogger("project_debug_log")


class GlobalExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            project_debug_log.exception("Unhandled exception for %s %s", request.method, request.path)
            raise