from ..schemas import Category, Finding, ParsedPage, Severity
import re

from .helpers import CRITICAL, MINOR, Check, finding_factory, plural, sample, verb

finding = finding_factory(Category.ACCESSIBILITY)

VAGUE_LINK_TEXT = {"click here", "here", "read more", "more", "link", "this", "learn more"}

GENERIC_ALT = {
    "image", "images", "img", "photo", "picture", "pic", "logo", "icon",
    "graphic", "banner", "thumbnail", "untitled", "alt", "alt text", "spacer",
}

FILENAME_ALT = re.compile(r"\.(png|jpe?g|gif|svg|webp|avif|bmp|ico)$", re.I)


def check_image_alt(page: ParsedPage) -> list[Finding]:
    if not page.images:
        return []

    missing = [image for image in page.images if image.alt is None]
    if missing:
        return [
            finding(
                Severity.ERROR,
                f"{len(missing)} of {plural(len(page.images), 'image')} "
                f"{verb(len(missing), 'has', 'have')} no alt attribute",
                "Screen readers announce the file name instead, or skip the image.",
                sample([image.src for image in missing]),
                'Describe each image, or use alt="" if it is purely decorative.',
            )
        ]
    return [
        finding(
            Severity.PASS,
            f"All {plural(len(page.images), 'image')} "
            f"{verb(len(page.images), 'has', 'have')} alt text",
        )
    ]


def check_lang(page: ParsedPage) -> list[Finding]:
    if not page.lang:
        return [
            finding(
                Severity.ERROR,
                "No lang attribute on <html>",
                "Screen readers cannot pick the right pronunciation rules.",
                recommendation='Add lang="en" (or the page\'s actual language) to <html>.',
            )
        ]
    return [finding(Severity.PASS, "Page language declared", evidence=page.lang)]


def check_heading_order(page: ParsedPage) -> list[Finding]:
    levels = [level for level, _ in page.headings]
    if not levels:
        return []

    skips = []
    previous = levels[0]
    for index, level in enumerate(levels[1:], start=1):
        if level > previous + 1:
            skips.append(f"h{previous} -> h{level} ({page.headings[index][1][:50]!r})")
        previous = level

    if skips:
        return [
            finding(
                Severity.WARNING,
                f"Heading levels skip {plural(len(skips), 'time')}",
                "Jumping levels breaks the document outline people navigate by.",
                sample(skips),
                "Step one level at a time; style with CSS, not heading level.",
            )
        ]
    return [finding(Severity.PASS, "Heading hierarchy is sequential")]


def check_link_text(page: ParsedPage) -> list[Finding]:
    vague = [link for link in page.links if link.text.lower().strip(" .!>") in VAGUE_LINK_TEXT]
    if vague:
        return [
            finding(
                Severity.WARNING,
                f"{plural(len(vague), 'link')} {verb(len(vague), 'has', 'have')} non-descriptive text",
                "People navigating by link list hear only the link text, without surrounding context.",
                sample([f"{link.text!r} -> {link.url}" for link in vague]),
                "Make the link text describe its destination.",
            )
        ]

    empty = [link for link in page.links if not link.text]
    if empty:
        return [
            finding(
                Severity.WARNING,
                f"{plural(len(empty), 'link')} {verb(len(empty), 'has', 'have')} no text",
                "Icon-only links need an accessible name.",
                sample([link.url for link in empty]),
                "Add visually hidden text or an aria-label.",
            )
        ]
    return []


def check_viewport(page: ParsedPage) -> list[Finding]:
    if not page.viewport:
        return [
            finding(
                Severity.WARNING,
                "No viewport meta tag",
                "Mobile browsers fall back to a desktop-width layout, forcing zoom.",
                recommendation='Add <meta name="viewport" content="width=device-width, initial-scale=1">.',
            )
        ]

    viewport = page.viewport.replace(" ", "")
    if "user-scalable=no" in viewport or "maximum-scale=1" in viewport:
        return [
            finding(
                Severity.WARNING,
                "Viewport blocks zooming",
                "Disabling zoom locks out people who rely on it to read.",
                page.viewport,
                "Drop user-scalable=no and maximum-scale.",
            )
        ]
    return [finding(Severity.PASS, "Responsive viewport declared")]


def check_alt_quality(page: ParsedPage) -> list[Finding]:
    described = [image for image in page.images if image.alt]
    if not described:
        return []

    useless = [
        image
        for image in described
        if image.alt.strip().lower() in GENERIC_ALT or FILENAME_ALT.search(image.alt.strip())
    ]
    if useless:
        return [
            finding(
                Severity.WARNING,
                f"{plural(len(useless), 'image')} {verb(len(useless), 'has', 'have')} placeholder alt text",
                "An alt attribute that names the file or says 'image' passes automated checks but tells a screen reader user nothing.",
                sample([f"{image.alt!r} on {image.src}" for image in useless]),
                "Describe what the image shows, or use alt=\"\" if it is decorative.",
            )
        ]
    return [finding(Severity.PASS, "Alt text is descriptive")]


CHECKS = [
    Check("Image alt text", check_image_alt, CRITICAL),
    Check("Alt text quality", check_alt_quality, CRITICAL),
    Check("Page language", check_lang, CRITICAL),
    Check("Heading order", check_heading_order),
    Check("Link text", check_link_text),
    Check("Mobile viewport", check_viewport, CRITICAL),
]
