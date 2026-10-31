"""Public GitHub intake using a pinned commit archive, without invoking Git."""
import re
import json
import time
from pathlib import Path
import httpx
from .archive import MAX_COMPRESSED

PATTERN = re.compile(r'^https://github\.com/([A-Za-z0-9_-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$')

def parse_url(url: str) -> tuple[str, str]:
    match = PATTERN.fullmatch(url.strip())
    if not match or match[2] in ('.', '..'):
        raise ValueError('Use a public https://github.com/owner/repository URL')
    return match[1], match[2]

def retrieve(url: str, output: Path, cancelled=lambda: False) -> dict:
    owner, repository = parse_url(url)
    started = time.monotonic()
    # Ignore machine proxies, credentials, cookies and git configuration. No redirects.
    with httpx.Client(timeout=httpx.Timeout(30, connect=10), trust_env=False, follow_redirects=False,
                      headers={'User-Agent': 'Repo-Intelligence-local', 'Accept': 'application/vnd.github+json'}) as client:
        with client.stream('GET', f'https://api.github.com/repos/{owner}/{repository}/commits/HEAD') as response:
            if response.status_code != 200:
                raise ValueError('Public repository unavailable or GitHub API rate limit reached')
            metadata = bytearray()
            for chunk in response.iter_bytes(65536):
                if cancelled(): raise InterruptedError('Cancelled')
                if time.monotonic()-started>120: raise ValueError('GitHub retrieval time limit reached')
                metadata.extend(chunk)
                if len(metadata)>2*1024*1024: raise ValueError('GitHub commit metadata limit reached')
        sha = json.loads(metadata).get('sha', '')
        if not re.fullmatch(r'[a-f0-9]{40}', sha):
            raise ValueError('GitHub did not return a commit identity')
        size = 0
        with client.stream('GET', f'https://codeload.github.com/{owner}/{repository}/zip/{sha}') as archive:
            if archive.status_code != 200:
                raise ValueError('GitHub source archive unavailable')
            with output.open('xb') as stream:
                for chunk in archive.iter_bytes(65536):
                    if cancelled():
                        raise InterruptedError('Cancelled')
                    if time.monotonic()-started>120:
                        raise ValueError('GitHub retrieval time limit reached')
                    size += len(chunk)
                    if size > MAX_COMPRESSED:
                        raise ValueError('GitHub archive exceeds the 50 MiB intake limit')
                    stream.write(chunk)
    return {'kind': 'github', 'url': f'https://github.com/{owner}/{repository}', 'commit': sha}
