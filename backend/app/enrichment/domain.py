import asyncio
import socket
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from ..config import settings
from ..schemas import DomainInfo

RDAP_BASE = "https://rdap.org"
RDAP_HEADERS = {"Accept": "application/rdap+json"}

DNS_PROVIDERS = {
    "cloudflare": "Cloudflare",
    "awsdns": "AWS Route 53",
    "azure-dns": "Azure DNS",
    "googledomains": "Google Domains",
    "google.com": "Google Cloud DNS",
    "nsone.net": "NS1",
    "domaincontrol.com": "GoDaddy",
    "registrar-servers.com": "Namecheap",
    "digitalocean.com": "DigitalOcean",
    "vercel-dns.com": "Vercel",
    "akam.net": "Akamai",
    "dnsimple.com": "DNSimple",
    "dnsmadeeasy.com": "DNS Made Easy",
    "ultradns": "UltraDNS",
    "wordpress.com": "WordPress.com",
    "shopify.com": "Shopify",
    "squarespacedns.com": "Squarespace",
    "wixdns.net": "Wix",
    "netlify.com": "Netlify",
    "name-services.com": "Network Solutions",
}


def registrable_domain(url: str) -> str:
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    parts = host.split(".")
    if len(parts) > 2 and parts[-2] in {"co", "com", "org", "net", "gov", "ac", "edu"}:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def registrar_name(payload: dict) -> str | None:
    for entity in payload.get("entities", []):
        if "registrar" not in entity.get("roles", []):
            continue
        for field in entity.get("vcardArray", [None, []])[1]:
            if field[0] == "fn":
                return field[3]
    return None


def match_providers(names: list[str]) -> str | None:
    joined = " ".join(names).lower()
    matched = {provider for marker, provider in DNS_PROVIDERS.items() if marker in joined}
    return " + ".join(sorted(matched)) if matched else None


async def resolve_ips(host: str) -> list[str]:
    try:
        infos = await asyncio.to_thread(socket.getaddrinfo, host, None)
    except socket.gaierror:
        return []
    return sorted({info[4][0] for info in infos})


async def lookup_hosting_provider(client: httpx.AsyncClient, ip: str) -> str | None:
    try:
        response = await client.get(f"{RDAP_BASE}/ip/{ip}")
        if response.status_code != 200:
            return None
        payload = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    for entity in payload.get("entities", []):
        for field in entity.get("vcardArray", [None, []])[1]:
            if field[0] == "fn":
                return field[3]
    return payload.get("name") or payload.get("handle")


async def lookup(url: str) -> DomainInfo:
    domain = registrable_domain(url)
    host = (urlparse(url).hostname or domain).lower()
    info = DomainInfo(domain=domain)

    info.ip_addresses = await resolve_ips(host)

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=settings.rdap_timeout,
            headers={**RDAP_HEADERS, "User-Agent": settings.user_agent},
        ) as client:
            response = await client.get(f"{RDAP_BASE}/domain/{domain}")
            if response.status_code == 404:
                info.lookup_error = f"No registry record found for {domain}."
                return info
            if response.status_code != 200:
                info.lookup_error = f"Registry lookup returned HTTP {response.status_code}."
                return info

            payload = response.json()
            events = {e.get("eventAction"): e.get("eventDate") for e in payload.get("events", [])}
            registered = parse_date(events.get("registration"))
            expires = parse_date(events.get("expiration"))
            updated = parse_date(events.get("last changed"))
            now = datetime.now(timezone.utc)

            info.registrar = registrar_name(payload)
            info.registered_on = registered.date().isoformat() if registered else None
            info.expires_on = expires.date().isoformat() if expires else None
            info.updated_on = updated.date().isoformat() if updated else None
            info.age_days = (now - registered).days if registered else None
            info.expires_in_days = (expires - now).days if expires else None
            info.status = payload.get("status", [])
            info.nameservers = [
                ns["ldhName"].lower().rstrip(".")
                for ns in payload.get("nameservers", [])
                if ns.get("ldhName")
            ]
            info.dns_provider = match_providers(info.nameservers)
            info.dnssec = payload.get("secureDNS", {}).get("delegationSigned")

            if info.ip_addresses:
                info.hosting_provider = await lookup_hosting_provider(client, info.ip_addresses[0])

    except httpx.TimeoutException:
        info.lookup_error = f"Registry lookup timed out after {settings.rdap_timeout:.0f}s."
    except httpx.HTTPError as exc:
        info.lookup_error = f"Registry lookup failed: {exc}"
    except ValueError:
        info.lookup_error = "Registry returned a malformed response."

    return info
