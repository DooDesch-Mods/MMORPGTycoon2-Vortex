"""Package the Vortex extension and prepare its release.

package: build dist/ (ZIP, SHA256SUMS.txt, notes.md) from extension/ and CHANGELOG.md.
nexus:   read-only check that the API key reaches the Nexus file; prints whether the version is new.
changelog: write the version changelog on Nexus once, then read it back.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import sys
import urllib.error
import urllib.request
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / 'extension'
DIST = ROOT / 'dist'
# Nexus page https://www.nexusmods.com/site/mods/2465, file "MMORPG Tycoon 2 Vortex Extension".
NEXUS = {'domain': 'site', 'page_id': 2465, 'mod_uid': '9856949946785', 'file_id': '8170257'}
API = 'https://api.nexusmods.com/v3'
# Fixed entry time and mode, so the same sources always give the same ZIP bytes.
ENTRY_TIME = (2026, 1, 1, 0, 0, 0)
ENTRY_MODE = 0o100644 << 16
FILES = ('index.js', 'info.json', 'gameart.png', 'package.json')


def log(level, message):
    print(f'{level}: {message}', file=sys.stderr if level == 'error' else sys.stdout)


def output(values):
    if destination := os.environ.get('GITHUB_OUTPUT'):
        with open(destination, 'a', encoding='utf-8') as stream:
            for name, value in values.items():
                delimiter = 'output_' + uuid.uuid4().hex
                stream.write(f'{name}<<{delimiter}\n{value}\n{delimiter}\n')


def semver(value):
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', value):
        raise ValueError('Expected version MAJOR.MINOR.PATCH: ' + value)
    return tuple(int(part) for part in value.split('.'))


def changelog_section(version):
    text = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')
    matches = list(re.finditer(r'^## ' + re.escape(version) + r'\s*$', text, re.M))
    if len(matches) != 1:
        raise ValueError(f'CHANGELOG.md: expected exactly one section "## {version}", found {len(matches)}')
    rest = text[matches[0].end():]
    end = re.search(r'^## ', rest, re.M)
    notes = (rest[:end.start()] if end else rest).strip()
    if not re.search(r'^- \S', notes, re.M):
        raise ValueError(f'CHANGELOG.md: section {version} has no release notes')
    return notes


def plain(markdown):
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', markdown)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return re.sub(r'^#{1,6}\s+', '', text, flags=re.M).strip()


def bbcode(markdown):
    """Headings become bold lines, bullets become [list] items; the notes use no nested lists."""
    text = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'[url=\2]\1[/url]', markdown)
    text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    result, in_list = [], False
    for line in text.splitlines():
        bullet = re.match(r'^[-*]\s+(.+)', line)
        if bullet and not in_list:
            result.append('[list]')
        if not bullet and in_list:
            result.append('[/list]')
        in_list = bool(bullet)
        heading = re.match(r'^#{1,6}\s+(.+)$', line)
        result.append('[*]' + bullet[1] if bullet else f'[b]{heading[1]}[/b]' if heading else line)
    if in_list:
        result.append('[/list]')
    return '\n'.join(result).strip()


def package(tag):
    info = json.loads((EXTENSION / 'info.json').read_text(encoding='utf-8'))
    version = info['version']
    semver(version)
    if not isinstance(info['gameId'], int):
        raise ValueError('Nexus gameId must be numeric')
    if tag and tag != 'v' + version:
        raise ValueError(f'Tag {tag} differs from extension/info.json version {version}')
    art = (EXTENSION / 'gameart.png').read_bytes()
    # A PNG stores width and height as big-endian integers right after the IHDR chunk type.
    if art[12:16] != b'IHDR' or struct.unpack('>II', art[16:24]) != (640, 360):
        raise ValueError('Game art must be a 640x360 PNG')
    if len(art) > 1024 * 1024:
        raise ValueError('Game art exceeds 1 MB')
    notes = changelog_section(version)
    DIST.mkdir(exist_ok=True)
    archive = DIST / f'MMORPGTycoon2-Vortex-{version}.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as stream:
        for name, source in [(n, EXTENSION / n) for n in FILES] + [('LICENSE', ROOT / 'LICENSE'), ('README.md', ROOT / 'README.md')]:
            entry = zipfile.ZipInfo(name, ENTRY_TIME)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3  # Unix, whatever the build host is
            entry.external_attr = ENTRY_MODE
            stream.writestr(entry, source.read_bytes())
    with zipfile.ZipFile(archive) as stream:
        if stream.testzip():
            raise ValueError('ZIP CRC failed')
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (DIST / 'SHA256SUMS.txt').write_text(f'{digest}  {archive.name}\n', encoding='utf-8')
    (DIST / 'notes.md').write_text(notes + '\n', encoding='utf-8')
    (DIST / 'notes.plain.txt').write_text(plain(notes) + '\n', encoding='utf-8')
    output({'version': version, 'filename': str(archive), 'title': f'MMORPG Tycoon 2 Vortex Extension {version}',
            'description': bbcode(notes)})
    log('info', f'packaged {archive.name}, {archive.stat().st_size} bytes, sha256 {digest}')
    return version


def request(url, method='GET', body=None):
    key = os.environ.get('NEXUSMODS_API_KEY', '').strip()
    if not key:
        raise ValueError('NEXUSMODS_API_KEY is empty or not visible to this repository; add the organization secret for it')
    data = None if body is None else json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, method=method, headers={
        'Accept': 'application/json', 'Content-Type': 'application/json', 'apikey': key, 'User-Agent': 'MT2-Vortex-CI'})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        # The body can hold account details; endpoint and status identify the failure.
        raise RuntimeError(f'Nexus {method} {url} failed: HTTP {error.code}; inspect the destination before retrying a write') from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f'Nexus {method} {url} failed ({type(error).__name__}); inspect the destination before retrying a write') from None


def nexus_status(version):
    """Return 'ready' for a new version or 'already-present'; fail on a wrong file or an older version."""
    files = request(f"{API}/mods/{NEXUS['mod_uid']}/files")['data']['mod_files']
    if not any(str(row['id']) == NEXUS['file_id'] for row in files):
        raise ValueError('Nexus file ID does not belong to the configured mod')
    versions = request(f"{API}/mod-files/{NEXUS['file_id']}/versions")['data']['versions']
    if not versions:
        raise ValueError('Nexus file has no existing version; check its file ID')
    if any(row['version'] == version for row in versions):
        return 'already-present'
    for row in versions:
        if semver(row['version']) >= semver(version):
            raise ValueError('Release version is older than a version already on Nexus: ' + row['version'])
    return 'ready'


def normalized(value, html_encoded=False):
    import html
    lines = [line for item in value for line in item.splitlines()] if isinstance(value, list) else value.splitlines()
    if html_encoded:
        lines = [html.unescape(line) for line in lines]
    return ' '.join(re.sub(r'^\s*[-*]\s+', '', line).strip() for line in lines if line.strip())


def sync_changelog(version):
    """Write the version changelog once: read through v1, write through v3, read back."""
    text = (DIST / 'notes.plain.txt').read_text(encoding='utf-8').strip()
    url = f"https://api.nexusmods.com/v1/games/{NEXUS['domain']}/mods/{NEXUS['page_id']}/changelogs.json"

    def state():
        rows = request(url).get(version, [])
        if not rows:
            return 'missing'
        if normalized(rows, True) == normalized(text):
            return 'confirmed'
        raise ValueError(f'Nexus changelog {version} already contains different text; refusing to append a duplicate')

    if state() == 'confirmed':
        log('info', f'Nexus changelog {version} already matches; nothing written')
        return
    request(f"{API}/mods/{NEXUS['mod_uid']}/changelogs", 'POST', {'version': version, 'changelog': text})
    if state() != 'confirmed':
        raise RuntimeError('Nexus accepted the changelog write, but readback is missing; inspect the destination before retrying')
    log('info', f'Nexus changelog {version} written and read back')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest='command', required=True)
    command = commands.add_parser('package')
    command.add_argument('--tag', help='release tag that must equal v<version>')
    commands.add_parser('nexus')
    commands.add_parser('changelog')
    args = parser.parse_args()
    version = json.loads((EXTENSION / 'info.json').read_text(encoding='utf-8'))['version']
    if args.command == 'package':
        package(args.tag)
    elif args.command == 'nexus':
        status = nexus_status(version)
        output({'status': status})
        log('info', f'Nexus file reachable with the API key; version {version} is {status}')
    else:
        sync_changelog(version)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, RuntimeError, zipfile.BadZipFile) as error:
        log('error', str(error))
        sys.exit(1)
