import copy
import importlib.util
import json
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
import PIL
from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location('assetlib', Path(__file__).resolve().parents[1] / 'tools/assets/assetlib.py')
assets = importlib.util.module_from_spec(spec); spec.loader.exec_module(assets)


class AssetTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'source.txt').write_text('Procedural fixture source')
        image = Image.new('RGBA', (32, 16))
        draw = ImageDraw.Draw(image)
        draw.rectangle((2, 2, 13, 13), fill='gold'); draw.rectangle((18, 2, 29, 13), fill='gold')
        image.save(self.root / 'sheet.png')
        self.entry = {'id': 'star', 'revision': 1, 'parent': None, 'kind': 'sprite',
                      'source': 'source.txt', 'source_sha256': assets.sha(self.root / 'source.txt'),
                      'author': 'test fixture', 'license': 'project-authored', 'created_at': '2026-09-10',
                      'purpose': 'Sprite import regression', 'review_status': 'draft',
                      'sprite': {'frame_width': 16, 'frame_height': 16, 'frame_count': 2, 'fps': 8,
                                 'pivot': [8, 14], 'transparent_padding': 2, 'ground_line_tolerance': 0},
                      'exports': [{'path': 'sheet.png', 'sha256': assets.sha(self.root / 'sheet.png'),
                                   'max_bytes': 4096, 'width': 32, 'height': 16, 'alpha': 'required'}]}

    def validate(self, entries=None):
        return assets.validate(self.root, {'schema_version': 1, 'assets': entries or [self.entry]})

    def test_valid_frames_and_provenance_register_without_overwrite(self):
        result = self.validate(); self.assertTrue(result['passed'], result)
        self.assertEqual(result['assets'][0]['metadata']['sprite']['frames_checked'], 2)
        path = self.root / 'manifest.json'
        assets.register(self.root, path, self.entry)
        before = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            assets.register(self.root, path, self.entry)
        self.assertEqual(path.read_bytes(), before)

    def test_missing_provenance_and_changed_exports_fail(self):
        del self.entry['license']; self.assertFalse(self.validate()['passed'])
        self.entry['license'] = 'project-authored'
        (self.root / 'sheet.png').write_bytes((self.root / 'sheet.png').read_bytes() + b'changed')
        self.assertIn('hash changed', self.validate()['errors'][0])

    def test_frame_count_padding_and_ground_line_failures(self):
        self.entry['sprite']['frame_count'] = 3
        self.assertIn('frame grid', self.validate()['errors'][0])
        self.entry['sprite']['frame_count'] = 2
        self.entry['sprite']['transparent_padding'] = 3
        self.assertIn('padding', self.validate()['errors'][0])
        self.entry['sprite']['transparent_padding'] = 0
        image = Image.new('RGBA', (32, 16)); draw = ImageDraw.Draw(image)
        draw.rectangle((2, 2, 13, 13), fill='gold'); draw.rectangle((18, 2, 29, 10), fill='gold')
        image.save(self.root / 'sheet.png'); self.entry['exports'][0]['sha256'] = assets.sha(self.root / 'sheet.png')
        self.assertIn('ground line', self.validate()['errors'][0])

    def test_lineage_cycle_and_missing_parent(self):
        self.entry['parent'] = 'star@2'
        self.assertIn('missing parent', ' '.join(self.validate()['errors']))
        second = copy.deepcopy(self.entry); second['revision'] = 2; second['parent'] = 'star@1'
        self.assertIn('cyclic', ' '.join(self.validate([self.entry, second])['errors']))

    def test_path_escape_symlinks_and_executable_svg_are_refused(self):
        self.entry['source'] = '../outside'
        self.assertIn('Invalid project asset path', self.validate()['errors'][0])
        (self.root / 'link').symlink_to(self.root / 'sheet.png')
        with self.assertRaises(ValueError): assets.asset_path(self.root, 'link')
        (self.root / 'bad.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>')
        with self.assertRaisesRegex(ValueError, 'Executable'): assets.inspect_file(self.root / 'bad.svg')

    def test_audio_clipping_and_loop_boundary_are_measured(self):
        p = self.root / 'loop.wav'
        with wave.open(str(p), 'wb') as out:
            out.setparams((1, 2, 8000, 0, 'NONE', 'not compressed'))
            out.writeframes(struct.pack('<hhhh', 32767, 0, 0, -32768))
        metadata = assets.inspect_file(p)
        self.assertEqual(metadata['peak'], 1)
        self.assertGreater(metadata['loop_boundary_delta'], 1.9)
        self.entry.update(kind='audio', exports=[{'path': 'loop.wav', 'sha256': assets.sha(p), 'max_bytes': 1024, 'loop': True}])
        self.assertIn('peak', self.validate()['errors'][0])
        self.entry['exports'][0]['max_peak'] = 1
        self.assertIn('boundary', self.validate()['errors'][0])

    def test_runtime_budget_and_alpha_requirements(self):
        self.entry['exports'][0]['max_bytes'] = 1
        self.assertIn('size budget', self.validate()['errors'][0])
        self.entry['exports'][0]['max_bytes'] = 4096
        image = Image.new('RGB', (32, 16), 'gold'); image.save(self.root / 'sheet.png')
        self.entry['exports'][0]['sha256'] = assets.sha(self.root / 'sheet.png')
        self.assertIn('transparent', self.validate()['errors'][0])

    def test_supported_raster_content_and_alpha(self):
        for suffix, format in [('.png', 'PNG'), ('.jpg', 'JPEG'), ('.jpeg', 'JPEG'), ('.webp', 'WEBP')]:
            with self.subTest(format=format, suffix=suffix):
                p = self.root / ('valid' + suffix)
                Image.new('RGB', (8, 8), 'gold').save(p, format=format)
                result = assets.inspect_file(p)
                self.assertEqual((result['width'], result['height']), (8, 8))
                self.assertFalse(result['has_transparency'])
        self.assertTrue(assets.inspect_file(self.root / 'sheet.png')['has_transparency'])

    def test_unsupported_or_mismatched_content_cannot_reach_decode(self):
        for format in ['BMP', 'GIF', 'JPEG']:
            with self.subTest(format=format):
                p = self.root / 'disguised.png'
                Image.new('RGB', (32, 16), 'white').save(p, format=format)
                with self.assertRaises(OSError): assets.inspect_file(p)
                with self.assertRaises(OSError): assets.sprite_checks(p, self.entry['sprite'])
        # JPEG dispatch can identify MPO; the result must still match the selected export.
        with patch('PIL.Image.open') as opened:
            opened.return_value.__enter__.return_value.format = 'MPO'
            with self.assertRaisesRegex(ValueError, 'extension'):
                assets.inspect_file(self.root / 'sheet.png')
            opened.return_value.__enter__.return_value.load.assert_not_called()

    def test_old_pillow_is_rejected_before_opening_a_file(self):
        for version in ['12.2.0', '12.3.0', '13.0.0rc1']:
            with self.subTest(version=version), patch.object(PIL, '__version__', version), patch('PIL.Image.open') as opened:
                with self.assertRaisesRegex(ValueError, 'Pillow 13'):
                    assets.inspect_file(self.root / 'sheet.png')
                with self.assertRaisesRegex(ValueError, 'Pillow 13'):
                    assets.sprite_checks(self.root / 'sheet.png', self.entry['sprite'])
                opened.assert_not_called()

    def test_multiframe_and_oversized_rasters_are_rejected(self):
        p = self.root / 'animated.png'
        frames = [Image.new('RGBA', (32, 16), color) for color in ['red', 'blue']]
        frames[0].save(p, save_all=True, append_images=frames[1:], duration=100, loop=0)
        for inspect in [lambda: assets.inspect_file(p), lambda: assets.sprite_checks(p, self.entry['sprite'])]:
            with self.assertRaisesRegex(ValueError, 'multi-frame'): inspect()
        with patch.object(assets, 'MAX_PIXELS', 16):
            with self.assertRaisesRegex(ValueError, 'limit'): assets.inspect_file(self.root / 'sheet.png')
            with self.assertRaisesRegex(ValueError, 'limit'): assets.sprite_checks(self.root / 'sheet.png', self.entry['sprite'])


if __name__ == '__main__': unittest.main()
