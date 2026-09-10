#!/usr/bin/env python3
"""Project-owned asset revisions, provenance, import contracts, and inspection."""
import argparse
import hashlib
import html
import json
import math
import os
import re
import struct
import sys
import tempfile
import wave
from pathlib import Path
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
RASTER = {'.png', '.jpg', '.jpeg', '.webp'}
KINDS = {'image', 'sprite', 'texture', 'vector', 'audio', 'model'}
ID = re.compile(r'^[a-z0-9][a-z0-9_-]{0,79}$')


def asset_path(root, relative):
    rel = Path(relative)
    if rel.is_absolute() or not rel.parts or '..' in rel.parts or rel.parts[0] == '.git':
        raise ValueError(f'Invalid project asset path: {relative}')
    current = root
    for part in rel.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(f'Symlinked asset path: {relative}')
    return current


def sha(path):
    with path.open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()


def inspect_file(path):
    result = {'bytes': path.stat().st_size, 'sha256': sha(path), 'extension': path.suffix.lower()}
    if path.suffix.lower() in RASTER:
        from PIL import Image
        with Image.open(path) as image:
            if image.width * image.height > 16_777_216:
                raise ValueError('Inspection limit is 16,777,216 pixels per image; use a target-specific large-texture adapter')
            image.load()
            rgba = image.convert('RGBA')
            low, high = rgba.getchannel('A').getextrema()
            result.update(width=image.width, height=image.height, mode=image.mode,
                          has_transparency=low < 255, alpha_min=low, alpha_max=high,
                          content_bounds=rgba.getchannel('A').getbbox())
    elif path.suffix.lower() == '.svg':
        raw = path.read_text()
        if '<!DOCTYPE' in raw.upper() or '<!ENTITY' in raw.upper():
            raise ValueError('SVG external entities/DOCTYPE unsupported')
        root = ET.fromstring(raw)
        if root.tag.rsplit('}', 1)[-1] != 'svg':
            raise ValueError('Expected SVG root')
        for element in root.iter():
            if element.tag.rsplit('}', 1)[-1] in {'script', 'foreignObject'}:
                raise ValueError('Executable/embedded SVG content is not allowed')
            if element.tag.rsplit('}', 1)[-1] == 'style' and ('@import' in (element.text or '').lower() or
                    re.search(r'url\(\s*[\'\"]?(?!#)', element.text or '', re.I)):
                raise ValueError('External SVG styles unsupported')
            for key, value in element.attrib.items():
                key = key.rsplit('}', 1)[-1].lower()
                if key.startswith('on') or (key in {'href', 'src'} and not value.startswith('#')):
                    raise ValueError('SVG event handlers/external references unsupported')
                if 'url(' in value.lower() and not re.fullmatch(r'url\(#[\w-]+\)', value):
                    raise ValueError('External SVG paint reference unsupported')
        result['view_box'] = root.get('viewBox')
    elif path.suffix.lower() == '.wav':
        with wave.open(str(path), 'rb') as audio:
            channels, width, rate, frames = audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()
            result.update(channels=channels, sample_rate=rate, duration_seconds=frames / rate,
                          sample_width=width, frames=frames)
            if width != 2:
                raise ValueError('Audio peak/loop inspection requires PCM16 WAV')
            raw = audio.readframes(frames)
            samples = struct.unpack('<' + 'h' * (len(raw) // 2), raw)
            result['peak'] = max((abs(s) / 32768 for s in samples), default=0)
            result['rms'] = math.sqrt(sum((s / 32768) ** 2 for s in samples) / max(1, len(samples)))
            result['loop_boundary_delta'] = max((abs(samples[c] - samples[-channels + c]) / 32768
                                                   for c in range(channels)), default=0) if samples else 0
    elif path.suffix.lower() == '.gltf':
        model = json.loads(path.read_text())
        if model.get('asset', {}).get('version') != '2.0':
            raise ValueError('Expected glTF 2.0')
        result.update(meshes=len(model.get('meshes', [])), materials=len(model.get('materials', [])),
                      skins=len(model.get('skins', [])), animations=len(model.get('animations', [])))
        for item in model.get('buffers', []) + model.get('images', []):
            uri = item.get('uri', '')
            if uri.startswith('data:'):
                continue
            if uri:
                if ':' in uri or '?' in uri or '#' in uri:
                    raise ValueError('External glTF URI unsupported')
                if not asset_path(path.parent, uri).is_file():
                    raise ValueError('Missing glTF dependency: ' + uri)
        result['render_review'] = 'required_in_target_engine'
    else:
        raise ValueError('Unsupported format; use PNG/JPEG/WebP/SVG/PCM16 WAV/glTF for inspected exports')
    return result


def sprite_checks(path, spec):
    from PIL import Image
    width, height, count = spec['frame_width'], spec['frame_height'], spec['frame_count']
    if any(type(v) is not int or v <= 0 for v in [width, height, count]):
        raise ValueError('Sprite frame dimensions/count must be positive integers')
    if not isinstance(spec.get('fps'), (int, float)) or not 0 < spec['fps'] <= 240:
        raise ValueError('Sprite fps must be 0..240')
    pivot = spec.get('pivot')
    if not isinstance(pivot, list) or len(pivot) != 2 or not 0 <= pivot[0] <= width or not 0 <= pivot[1] <= height:
        raise ValueError('Sprite needs a pivot within the frame')
    with Image.open(path) as image:
        if image.width % width or image.height % height or image.width // width * (image.height // height) != count:
            raise ValueError('Sprite sheet dimensions do not match the declared complete frame grid')
        rgba = image.convert('RGBA')
        bounds, bottoms = [], []
        padding = spec.get('transparent_padding', 0)
        if type(padding) is not int or padding < 0 or padding * 2 >= min(width, height):
            raise ValueError('Invalid transparent padding')
        for index in range(count):
            x = index % (image.width // width) * width
            y = index // (image.width // width) * height
            box = rgba.crop((x, y, x + width, y + height)).getchannel('A').getbbox()
            if box is None:
                raise ValueError(f'Empty sprite frame {index}')
            if padding and (box[0] < padding or box[1] < padding or box[2] > width - padding or box[3] > height - padding):
                raise ValueError(f'Sprite frame {index} touches required transparent padding')
            bounds.append(box); bottoms.append(box[3])
        if 'ground_line_tolerance' in spec and max(bottoms) - min(bottoms) > spec['ground_line_tolerance']:
            raise ValueError('Sprite ground line moves beyond the declared tolerance')
        return {'frames_checked': count, 'frame_bounds': bounds,
                'ground_line_delta': max(bottoms) - min(bottoms), 'visual_motion_review': 'required'}


def validate(root, manifest):
    errors, inspected, keys, parents = [], [], set(), {}
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1 or not isinstance(manifest.get('assets'), list):
        return {'passed': False, 'errors': ['Expected schema_version 1 and assets list'], 'assets': []}
    for asset in manifest['assets']:
        if not isinstance(asset, dict):
            errors.append('Each asset must be an object'); continue
        key = f"{asset.get('id')}@{asset.get('revision')}"
        try:
            if not isinstance(asset.get('id'), str) or not ID.fullmatch(asset['id']) or type(asset.get('revision')) is not int or asset['revision'] < 1:
                raise ValueError('Asset needs a stable slug ID and positive revision')
            if key in keys:
                raise ValueError('Duplicate asset revision')
            if asset.get('parent') is not None and not isinstance(asset['parent'], str):
                raise ValueError('Parent must be an asset@revision string or null')
            keys.add(key); parents[key] = asset.get('parent')
            if asset.get('kind') not in KINDS:
                raise ValueError('Unsupported asset kind')
            for field in ['purpose', 'author', 'license', 'created_at']:
                if not isinstance(asset.get(field), str) or not asset[field].strip():
                    raise ValueError('Missing provenance field: ' + field)
            if asset.get('review_status') not in {'draft', 'reviewed', 'placeholder'}:
                raise ValueError('Set an explicit review_status')
            if asset.get('generation'):
                generation = asset['generation']
                if not isinstance(generation, dict):
                    raise ValueError('Generation provenance must be an object')
                if not generation.get('provider') or not generation.get('prompt'):
                    raise ValueError('Generated asset needs provider and actual prompt')
            for ref in asset.get('references', []):
                if not isinstance(ref, dict) or not ref.get('source') or not ref.get('permitted_use'):
                    raise ValueError('References need source and permitted_use')
            source = asset_path(root, asset['source'])
            if not source.is_file() or sha(source) != asset.get('source_sha256'):
                raise ValueError('Original source is missing or its hash changed')
            exports = asset.get('exports')
            if not isinstance(exports, list) or not exports:
                raise ValueError('At least one runtime export is required')
            for export in exports:
                if not isinstance(export, dict):
                    raise ValueError('Runtime export must be an object')
                file = asset_path(root, export['path'])
                if file == source:
                    raise ValueError('Keep editable source and runtime export paths separate')
                allowed = {'image': RASTER, 'sprite': {'.png', '.webp'}, 'texture': RASTER,
                           'vector': {'.svg'}, 'audio': {'.wav'}, 'model': {'.gltf'}}
                if file.suffix.lower() not in allowed[asset['kind']]:
                    raise ValueError('Runtime format does not match asset kind')
                budget = export.get('max_bytes')
                if type(budget) is not int or budget <= 0:
                    raise ValueError('Runtime export needs a positive max_bytes budget')
                if file.stat().st_size > budget:
                    raise ValueError(f'Runtime size budget exceeded: {file.stat().st_size} > {budget}')
                metadata = inspect_file(file)
                if metadata['sha256'] != export.get('sha256'):
                    raise ValueError('Runtime export hash changed: ' + export['path'])
                for dimension in ['width', 'height']:
                    if dimension in export and metadata.get(dimension) != export[dimension]:
                        raise ValueError('Export dimension mismatch: ' + dimension)
                if export.get('alpha') == 'required' and not metadata.get('has_transparency'):
                    raise ValueError('Export requires transparent pixels')
                if export.get('alpha') == 'opaque' and metadata.get('has_transparency'):
                    raise ValueError('Opaque export contains transparency')
                if asset['kind'] == 'sprite':
                    metadata['sprite'] = sprite_checks(file, asset['sprite'])
                if asset['kind'] == 'audio':
                    if metadata.get('peak', 2) > export.get('max_peak', 0.99):
                        raise ValueError('Audio peak exceeds budget or format is not inspected audio')
                    if export.get('loop') and metadata['loop_boundary_delta'] > export.get('max_loop_delta', 0.02):
                        raise ValueError('Audio loop has an excessive boundary discontinuity')
                inspected.append({'asset': key, 'path': export['path'], 'metadata': metadata})
        except (KeyError, TypeError, ValueError, OSError, ImportError, EOFError, wave.Error, ET.ParseError) as error:
            errors.append(f'{key}: {error}')
    for key in parents:
        chain, current = set(), key
        while current:
            if current in chain:
                errors.append(f'{key}: cyclic revision lineage'); break
            if current not in keys:
                errors.append(f'{key}: missing parent revision {current}'); break
            chain.add(current); current = parents.get(current)
    return {'passed': not errors, 'errors': errors, 'assets': inspected,
            'visual_review': 'separate review required; metadata checks do not establish art quality'}


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, delete=False) as file:
        json.dump(value, file, indent=2, ensure_ascii=False); file.write('\n')
        temp = Path(file.name)
    try:
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def register(root, manifest_path, entry):
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'schema_version': 1, 'assets': []}
    entry = json.loads(json.dumps(entry))
    entry['source_sha256'] = sha(asset_path(root, entry['source']))
    for export in entry['exports']:
        export['sha256'] = sha(asset_path(root, export['path']))
    manifest['assets'].append(entry)
    result = validate(root, manifest)
    if not result['passed']:
        raise ValueError('; '.join(result['errors']))
    atomic_json(manifest_path, manifest)
    return result


def catalog(root, manifest, output):
    result = validate(root, manifest)
    if not result['passed']:
        raise ValueError('; '.join(result['errors']))
    cards = []
    for asset in manifest['assets']:
        exported = asset_path(root, asset['exports'][0]['path'])
        url = html.escape(os.path.relpath(exported, output.parent), quote=True)
        if exported.suffix.lower() in RASTER | {'.svg'}:
            preview = f'<img src="{url}" alt="{html.escape(asset["purpose"], quote=True)}">'
        elif exported.suffix.lower() == '.wav':
            preview = f'<audio controls src="{url}"></audio>'
        else:
            preview = f'<a href="{url}">Inspect in target engine</a>'
        cards.append(f'<article>{preview}<h2>{html.escape(asset["id"])} · r{asset["revision"]}</h2><p>{html.escape(asset["purpose"])}</p><small>{html.escape(asset["author"])} · {html.escape(asset["license"])} · {html.escape(asset["review_status"])}</small></article>')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Asset library</title><style>body{font:16px system-ui;background:#111b25;color:#edf3f5;margin:32px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}article{padding:20px;background:#1d2c38;border-radius:16px}img{width:100%;height:220px;object-fit:contain;background:repeating-conic-gradient(#263d46 0% 25%,#1d3039 0% 50%) 0/20px 20px}small{color:#b8c5cc}a{color:#85e5dd}</style><h1>Asset library</h1><p>Validated metadata · review visual identity and motion separately.</p><main>'+''.join(cards)+'</main></html>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'register', 'catalog', 'inspect'])
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--manifest', default='assets/manifest.json')
    parser.add_argument('--entry', help='Project-relative JSON entry file to register')
    parser.add_argument('--file', help='Project-relative export file to inspect')
    parser.add_argument('--output', default='.agent/assets/index.html')
    args = parser.parse_args(); root = args.project.resolve()
    try:
        manifest_path = asset_path(root, args.manifest)
        if args.command == 'inspect':
            result = inspect_file(asset_path(root, args.file))
        elif args.command == 'register':
            result = register(root, manifest_path, json.loads(asset_path(root, args.entry).read_text()))
        else:
            manifest = json.loads(manifest_path.read_text())
            result = validate(root, manifest)
            if args.command == 'catalog':
                output = asset_path(root, args.output)
                if output.exists():
                    raise ValueError('Catalog output already exists; choose a new path')
                catalog(root, manifest, output); result['catalog'] = str(output)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if result.get('passed', True) else 1
    except (OSError, ValueError, TypeError, KeyError, ImportError) as error:
        print(json.dumps({'passed': False, 'errors': [str(error)]})); return 1


if __name__ == '__main__':
    sys.exit(main())
