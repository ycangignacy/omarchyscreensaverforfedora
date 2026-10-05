"""Installer ownership, upgrades and settings recovery — made by ycangignacy."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from argparse import Namespace
os.environ['GSETTINGS_BACKEND'] = 'memory'
from gi.repository import Gio
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('installer', ROOT/'install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        app = self.home/'data/fedora-ascii-screensaver'
        self.context = patch.multiple(installer, HOME=self.home, DATA=self.home/'data', CONFIG=self.home/'config', APP=app,
            UNIT=self.home/'config/systemd/user/fedora-ascii-screensaver.service',
            DESKTOP=self.home/'data/applications/local.fedora.asciisaver.desktop',
            BIN=self.home/'bin/fedora-screensaver',MARKER=app/'.installed-by-ycangignacy',STATE=app/'.gnome-settings.json')
        self.context.start()
        self.runner = patch.object(installer,'run')
        self.run = self.runner.start()
        self.args = Namespace(dry_run=False,no_autostart=True,idle_seconds=None,replace_blanking=False,disable_suspend=False)
    def tearDown(self):
        self.runner.stop();self.context.stop();self.temp.cleanup()
    def test_install_update_and_uninstall_keep_unrelated_files(self):
        unrelated=self.home/'keep.txt';unrelated.write_text('keep')
        installer.install(self.args)
        self.assertTrue(installer.MARKER.exists())
        self.assertTrue(os.access(installer.BIN,os.X_OK))
        self.assertIn(str(installer.APP),installer.DESKTOP.read_text())
        (installer.APP/'config.json').write_text('{"idle_seconds": 600}')
        installer.install(self.args)
        self.assertIn('600',(installer.APP/'config.json').read_text())
        installer.uninstall()
        self.assertFalse(installer.APP.exists())
        self.assertEqual(unrelated.read_text(),'keep')
    def test_unknown_existing_folder_is_not_overwritten(self):
        installer.APP.mkdir(parents=True)
        file=installer.APP/'keep.txt';file.write_text('original')
        with self.assertRaises(RuntimeError):installer.install(self.args)
        self.assertEqual(file.read_text(),'original')
        self.run.assert_not_called()
    def test_optional_settings_are_restored(self):
        desktop=Gio.Settings.new('org.gnome.desktop.session')
        power=Gio.Settings.new('org.gnome.settings-daemon.plugins.power')
        desktop.set_uint('idle-delay',600)
        power.set_string('sleep-inactive-ac-type','suspend')
        power.set_int('sleep-inactive-ac-timeout',900)
        self.args.replace_blanking=True;self.args.disable_suspend=True
        installer.install(self.args)
        self.assertEqual(desktop.get_uint('idle-delay'),0)
        self.assertEqual(power.get_string('sleep-inactive-ac-type'),'nothing')
        installer.uninstall()
        self.assertEqual(desktop.get_uint('idle-delay'),600)
        self.assertEqual(power.get_string('sleep-inactive-ac-type'),'suspend')
        self.assertEqual(power.get_int('sleep-inactive-ac-timeout'),900)
    def test_dry_run_changes_nothing(self):
        self.args.dry_run=True
        installer.install(self.args)
        self.assertFalse(installer.APP.exists())
        self.run.assert_not_called()

if __name__=='__main__':unittest.main()
