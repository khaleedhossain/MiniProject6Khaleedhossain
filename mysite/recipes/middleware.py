# INF601 - Advanced Programming in Python
# Khaleed Hossain
# Mini Project 6

import os

from django.http import HttpResponseForbidden


class AdminIPAllowlistMiddleware:
    """Restrict /admin/ to a configured set of client IPs.

    Set DJANGO_ADMIN_ALLOWED_IPS to a comma-separated list of IPs to turn
    this on (e.g. "1.2.3.4,5.6.7.8"). Left unset, it's a no-op -- admin
    stays reachable, which is the default until a specific IP (e.g. the
    instructor's) is known to allowlist.

    The dev box sits behind a reverse proxy (Cloudflare), so the real
    client IP arrives in X-Forwarded-For, not REMOTE_ADDR -- this only
    trusts that header because the proxy in front of us is the only way
    to reach this process at all, not because it's generally safe to trust
    client-supplied headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        raw = os.environ.get("DJANGO_ADMIN_ALLOWED_IPS", "")
        self.allowed = {ip.strip() for ip in raw.split(",") if ip.strip()}

    def __call__(self, request):
        if self.allowed and request.path.startswith("/admin/"):
            client_ip = self._client_ip(request)
            if client_ip not in self.allowed:
                return HttpResponseForbidden("Admin access restricted.")
        return self.get_response(request)

    @staticmethod
    def _client_ip(request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
