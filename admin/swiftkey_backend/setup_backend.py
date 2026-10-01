#!/usr/bin/env python3
"""Build the optional native SwiftKey backend; no downloads without --download."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent


def digest(path):
    """SHA-256 of a file."""
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def download(url, destination, expected):
    """Fetch a pinned HTTPS artifact and validate before using it."""
    if not url.startswith('https://'):
        raise ValueError('Only pinned HTTPS downloads are supported.')
    with urllib.request.urlopen(url, timeout=60) as response, destination.open('wb') as stream:
        shutil.copyfileobj(response, stream)
    if digest(destination) != expected:
        raise ValueError(f'SHA-256 mismatch: {destination.name}')
    return destination


def build(args):
    """Prepare into a new directory, compile, and run a native smoke test."""
    output = args.output.expanduser().resolve()
    if output.exists():
        raise ValueError('Output directory exists; select a new directory.')
    if not args.download and (args.engine_zip is None or args.deps_dir is None):
        raise ValueError('Use --engine-zip and --deps-dir for offline setup, or explicitly --download.')
    origin = json.loads((HERE / 'origin.json').read_text(encoding='utf-8'))
    dependencies = json.loads((HERE / 'dependencies.json').read_text(encoding='utf-8'))
    compiler = args.javac or shutil.which('javac')
    if not compiler and os.environ.get('JAVA_HOME'):
        candidate = Path(os.environ['JAVA_HOME']) / 'bin' / ('javac.exe' if os.name == 'nt' else 'javac')
        if candidate.is_file():
            compiler = str(candidate)
    java = shutil.which('java')
    if os.environ.get('JAVA_HOME'):
        candidate = Path(os.environ['JAVA_HOME']) / 'bin' / ('java.exe' if os.name == 'nt' else 'java')
        if candidate.is_file():
            java = str(candidate)
    if not compiler:
        raise ValueError('Building the backend requires a JDK 17+ (javac).')
    if not java:
        raise ValueError('Java 17+ is required to check the built backend.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='swiftkey_backend_', dir=output.parent) as temporary:
        work = Path(temporary)
        bundle = work / 'backend'
        for folder in ('engine', 'deps', 'classes', 'src'):
            (bundle / folder).mkdir(parents=True)
        archive = args.engine_zip
        if archive is None:
            print('Downloading the original Microsoft legacy release...')
            archive = download(origin['source_url'], work / 'SwiftKey.zip', origin['source_zip_sha256'])
        if digest(archive) != origin['source_zip_sha256']:
            raise ValueError('Original SwiftKey ZIP SHA-256 mismatch; expected 9.10.49.20 legacy release.')
        with zipfile.ZipFile(archive) as outer:
            candidates = [name for name in outer.namelist() if name.endswith('market-release-arm64-v8a.apk')]
            if len(candidates) != 1:
                raise ValueError('Original release must contain exactly one matching ARM64 APK.')
            with zipfile.ZipFile(io.BytesIO(outer.read(candidates[0]))) as apk:
                engine = apk.read('lib/arm64-v8a/libfluency-java-internal.so')
        library = bundle / 'engine' / 'libfluency-java-internal.so'
        library.write_bytes(engine)
        if digest(library) != origin['engine_sha256']:
            raise ValueError('Extracted native engine SHA-256 mismatch.')

        def dependency(item):
            target = bundle / 'deps' / item['filename']
            local = args.deps_dir / item['filename'] if args.deps_dir else None
            if local is not None and local.is_file():
                shutil.copyfile(local, target)
            elif args.download:
                download(item['binary_url'], target, item['sha256'])
            else:
                raise ValueError(f'Missing offline dependency: {item["filename"]}')
            if digest(target) != item['sha256']:
                raise ValueError(f'Dependency SHA-256 mismatch: {item["filename"]}')

        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(dependency, dependencies))
        source = bundle / 'src' / 'SwiftKeyNative.java'
        shutil.copyfile(HERE / source.name, source)
        compile_classpath = os.pathsep.join(str(path) for path in sorted((bundle / 'deps').glob('*.jar')))
        javac_args = ['-encoding', 'UTF-8', '--release', '17', '-cp', compile_classpath,
                      '-d', str(bundle / 'classes'), str(source)]
        command = [compiler] + javac_args
        subprocess.run(command, check=True)
        for filename in ('origin.json', 'dependencies.json'):
            target = bundle / 'engine' / filename if filename == 'origin.json' else bundle / filename
            shutil.copyfile(HERE / filename, target)
        # Fixture is synthetic, generated by the original engine, not extracted evidence.
        fixture = HERE / 'smoke_dynamic.lm'
        classpath = os.pathsep.join([str(bundle / 'classes'), str(bundle / 'deps' / '*')])
        result = subprocess.run([java, '-Xmx1536m', '-Dfile.encoding=UTF-8',
                                 '-Dorg.slf4j.simpleLogger.defaultLogLevel=error', '-cp', classpath,
                                 'SwiftKeyNative', 'extract', str(library), str(work / 'emuroot'),
                                 str(fixture), str(work / 'smoke.json')], check=True,
                                capture_output=True, text=True, timeout=180)
        if result.stdout:
            raise ValueError('Native smoke test produced unexpected stdout.')
        raw = json.loads((work / 'smoke.json').read_text(encoding='utf-8'))
        if raw['engine_version'] != origin['engine_version'] or len(raw['model']['words']) != 17:
            raise ValueError('Native smoke test did not match the synthetic fixture.')
        shutil.copytree(bundle, output)
    print(f'Backend ready: {output}')
    print('Set ALEAPP_SWIFTKEY_BACKEND to this directory. Runtime requires Java 17+ and works offline.')


def main():
    """CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New external backend directory')
    parser.add_argument('--download', action='store_true', help='Allow explicit downloads from Microsoft and Maven')
    parser.add_argument('--engine-zip', type=Path, help='Original Microsoft SwiftKey 9.10.49.20 ZIP')
    parser.add_argument('--deps-dir', type=Path, help='Directory of pinned Maven JARs, for offline setup')
    parser.add_argument('--javac', help='JDK 17+ javac executable')
    args = parser.parse_args()
    try:
        build(args)
    except (ValueError, OSError, KeyError, zipfile.BadZipFile, subprocess.SubprocessError) as error:
        print(f'Backend setup failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
