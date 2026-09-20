import ipaddress
import socket
from urllib.parse import urlparse, urlunparse

ALLOWED_SCHEMES = {"http", "https"}
INTERNAL_HOSTNAMES = {"localhost", "localhost.localdomain", "ip6-localhost"}
INTERNAL_HOST_SUFFIXES = (".localhost", ".local", ".internal", ".home", ".lan")


class UnsafeURL(Exception):
    pass


def normalize_url(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        raise UnsafeURL("URL is empty.")
    if "://" not in raw:
        raw = "https://" + raw

    parsed = urlparse(raw)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise UnsafeURL(f"Only http and https are supported (got '{parsed.scheme}').")
    if not parsed.hostname:
        raise UnsafeURL("URL has no hostname.")

    return urlunparse(
        (parsed.scheme, parsed.netloc, parsed.path or "/", parsed.params, parsed.query, "")
    )


def assert_public_host(url: str) -> None:
    host = urlparse(url).hostname
    if not host:
        raise UnsafeURL("URL has no hostname.")

    host = host.rstrip(".").lower()
    # Names without a DNS suffix are normally local-search-domain names.  Reject
    # them before resolution, along with common internal-only hostname suffixes.
    if (
        host in INTERNAL_HOSTNAMES
        or host.endswith(INTERNAL_HOST_SUFFIXES)
        or "." not in host and ":" not in host
    ):
        raise UnsafeURL(f"'{host}' is not a public hostname. Refusing to fetch.")

    try:
        addresses = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise UnsafeURL(f"Could not resolve '{host}'.") from exc

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global or ip.is_multicast:
            raise UnsafeURL(
                f"'{host}' resolves to a non-public address ({ip}). Refusing to fetch."
            )


def validate(raw: str) -> str:
    url = normalize_url(raw)
    assert_public_host(url)
    return url
