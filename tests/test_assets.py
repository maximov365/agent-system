import copy
import importlib.util
import json
import struct
import tempfile
import unittest
import wave
from pathlib import Path
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


if __name__ == '__main__': unittest.main()
