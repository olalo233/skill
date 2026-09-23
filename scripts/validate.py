#!/usr/bin/env python3
"""Cheap publication checks; Gitleaks is the separate secret scanner."""
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
errors = []
files = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others', '--exclude-standard', '-z']).decode().split('\0')
for relative in sorted(set(filter(None, files))):
    path = ROOT / relative
    if not path.exists():
        continue
    if path.is_symlink():
        errors.append(f'{relative}: symlinks are not distributable'); continue
    content = path.read_text(encoding='utf-8')
    for label, pattern in {
        'personal home path': r'/(?:Users|home)/[A-Za-z0-9_.-]+/',
        'private address': r'\b(?:10\.(?:\d+\.){2}\d+|192\.168\.\d+\.\d+|172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+)\b',
        'merge conflict': r'^(?:<<<<<<< |=======\s*$|>>>>>>> )',
        'private key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    }.items():
        if re.search(pattern, content, re.M): errors.append(f'{relative}: {label}')

skills = {p.parent.name: p for p in (ROOT / 'skills').glob('*/SKILL.md')}
for name, path in skills.items():
    text = path.read_text()
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        errors.append(f'{name}: missing frontmatter'); continue
    frontmatter = text.split('---', 2)[1]
    if not re.search(r'^name: ["\']?' + re.escape(name) + r'["\']?\s*$', frontmatter, re.M):
        errors.append(f'{name}: frontmatter name mismatch')
    if not re.search(r'^description: .+', frontmatter, re.M): errors.append(f'{name}: missing description')
for name, dependency in [('show-me','html'),('eli5','html'),('grill-me','grilling')]:
    if name in skills and dependency not in skills: errors.append(f'{name}: missing dependency {dependency}')

manifest = json.loads((ROOT / '.sync/upstreams.json').read_text())
covered = set()
for source in manifest['sources']:
    if not re.fullmatch(r'[a-f0-9]{40}', source['revision']): errors.append('Invalid upstream commit')
    for mapping in source['paths']:
        path = PurePosixPath(mapping['destination'])
        if path.is_absolute() or '..' in path.parts or path.parts[0] not in ('skills','licenses'):
            errors.append('Unsafe sync destination'); continue
        if not (ROOT / path).exists(): errors.append(f'Missing source destination: {path}')
        if path.parts[0] == 'skills': covered.add(path.parts[1])
if set(skills) != covered: errors.append('Skills and upstream manifest differ')

assets = ROOT / 'skills/html/design-system'
for filename in ['document.css','theme.css','theme.js','math-copy.js','component-samples.html']:
    if not (assets / filename).is_file(): errors.append(f'Missing HTML asset: {filename}')
for filename in ['component-samples.html','document.css']:
    text = (assets / filename).read_text()
    refs = re.findall(r'(?:src|href)=["\'](\./[^"\']+)', text) + re.findall(r'@import url\(["\'](\./[^"\']+)', text)
    for ref in refs:
        if not (assets / ref).is_file(): errors.append(f'{filename}: broken asset {ref}')
if errors:
    print('\n'.join(errors)); raise SystemExit(1)
print(f'Validated {len(skills)} skills, upstream mappings, portable paths and HTML assets.')
