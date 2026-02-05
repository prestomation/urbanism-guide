#!/usr/bin/env python3
"""
Check for broken links to The Urbanist (theurbanist.org).

The Urbanist sometimes returns soft 404s (HTTP 200 with "Page Not Found" content)
instead of proper HTTP 404 responses. This script checks both.
"""

import re
import sys
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError


def find_urbanist_urls(repo_root: Path) -> dict[str, list[tuple[int, str]]]:
    """
    Find all Urbanist URLs in the repository.

    Returns:
        dict mapping file paths to list of (line_number, url) tuples
    """
    url_pattern = re.compile(r'https?://(?:www\.)?theurbanist\.org[^\s"\'<>\)]*')
    results = {}

    # Search in content and data directories
    search_paths = [
        repo_root / "content",
        repo_root / "data",
    ]

    extensions = {'.md', '.yaml', '.yml', '.html'}

    for search_path in search_paths:
        if not search_path.exists():
            continue

        for file_path in search_path.rglob('*'):
            if file_path.suffix not in extensions:
                continue
            if not file_path.is_file():
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
            except Exception:
                continue

            file_urls = []
            for line_num, line in enumerate(content.splitlines(), 1):
                for match in url_pattern.finditer(line):
                    url = match.group(0).rstrip('.,;:')
                    file_urls.append((line_num, url))

            if file_urls:
                rel_path = str(file_path.relative_to(repo_root))
                results[rel_path] = file_urls

    return results


def check_url(url: str, retries: int = 2) -> tuple[bool, str]:
    """
    Check if a URL is valid (not a 404 or soft 404).

    Returns:
        tuple: (is_valid, error_message or empty string)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; urbanism-guide-link-checker/1.0)'
    }

    for attempt in range(retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')

                # Check for soft 404 indicators in the page content
                soft_404_patterns = [
                    'Page Not Found',
                    'page not found',
                    '404 - Not Found',
                    "Sorry, we couldn't find",
                    'This page doesn\'t exist',
                    'Nothing was found',
                    'Oops! That page can\'t be found',
                ]

                for pattern in soft_404_patterns:
                    if pattern in content:
                        # Check if it's in the title or main content area
                        # to avoid false positives from sidebar/footer text
                        if f'<title>{pattern}' in content or \
                           f'<h1>{pattern}' in content or \
                           f'<h1 class' in content and pattern in content[:5000]:
                            return False, f"Soft 404 detected (page contains '{pattern}')"

                return True, ""

        except HTTPError as e:
            if e.code == 404:
                return False, f"HTTP 404 Not Found"
            elif e.code in (429, 503):  # Rate limited or service unavailable
                if attempt < retries:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return False, f"HTTP {e.code} (after {retries + 1} attempts)"
            else:
                return False, f"HTTP {e.code}"

        except URLError as e:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return False, f"Connection error: {e.reason}"

        except Exception as e:
            return False, f"Error: {str(e)}"

    return False, "Max retries exceeded"


def main():
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    print("Checking Urbanist links for broken URLs...")
    print()

    # Find all URLs
    url_map = find_urbanist_urls(repo_root)

    if not url_map:
        print("No Urbanist URLs found in the repository.")
        sys.exit(0)

    # Deduplicate URLs while tracking their locations
    unique_urls: dict[str, list[tuple[str, int]]] = {}
    for file_path, urls in url_map.items():
        for line_num, url in urls:
            if url not in unique_urls:
                unique_urls[url] = []
            unique_urls[url].append((file_path, line_num))

    print(f"Found {len(unique_urls)} unique Urbanist URLs across {len(url_map)} files")
    print()

    # Check each URL
    broken_links = []
    checked = 0

    for url, locations in unique_urls.items():
        checked += 1
        print(f"  [{checked}/{len(unique_urls)}] Checking: {url[:70]}...")

        is_valid, error = check_url(url)

        if not is_valid:
            broken_links.append((url, error, locations))
            print(f"    BROKEN: {error}")
        else:
            print(f"    OK")

        # Rate limiting - be nice to the server
        time.sleep(0.5)

    print()

    # Report results
    if broken_links:
        print("=" * 60)
        print(f"BROKEN LINKS FOUND: {len(broken_links)}")
        print("=" * 60)
        print()

        for url, error, locations in broken_links:
            print(f"URL: {url}")
            print(f"Error: {error}")
            print("Found in:")
            for file_path, line_num in locations:
                print(f"  - {file_path}:{line_num}")
            print()

        sys.exit(1)
    else:
        print(f"All {len(unique_urls)} Urbanist links are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
