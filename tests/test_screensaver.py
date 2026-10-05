"""Idle monitor regressions: renderer exit, lock handling and child cleanup."""
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('screensaver', ROOT / 'app/screensaver.py')
saver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(saver)

class IdleMonitorTests(unittest.TestCase):
    def setUp(self):
        self.app = saver.IdleMonitor()
        self.app.locked = Mock(return_value=False)
        self.app.call = Mock(return_value=1000)
        self.app.bus = Mock()
        self.app.bus.call_sync.return_value.unpack.return_value = (False,)

    def test_renderer_runs_without_daemon_and_is_not_duplicated(self):
        with patch.object(saver.subprocess, 'Popen') as spawn:
            spawn.return_value.poll.return_value = None
            self.app.show()
            self.app.show()
            spawn.assert_called_once_with([saver.sys.executable, str(ROOT / 'app/screensaver.py')])

    def test_locked_session_does_not_launch_renderer(self):
        self.app.locked.return_value = True
        with patch.object(saver.subprocess, 'Popen') as spawn:
            self.app.show()
            spawn.assert_not_called()

    def test_dismiss_terminates_and_reaps_child(self):
        child = self.app.viewer = Mock()
        child.poll.return_value = None
        self.app.dismiss()
        child.terminate.assert_called_once()
        child.wait.assert_called_once_with(timeout=3)
        self.assertIsNone(self.app.viewer)
        self.app.dismiss()
        child.terminate.assert_called_once()

    def test_unresponsive_renderer_is_killed_and_reaped(self):
        child = self.app.viewer = Mock()
        child.poll.return_value = None
        child.wait.side_effect = [subprocess.TimeoutExpired('renderer', 3), 0]
        self.app.dismiss()
        child.kill.assert_called_once()
        self.assertEqual(child.wait.call_count, 2)

    def test_finished_child_is_reaped_before_next_idle_activation(self):
        self.app.viewer = Mock()
        self.app.viewer.poll.return_value = 0
        self.app.armed = False
        self.assertTrue(self.app.poll())
        self.assertIsNone(self.app.viewer)
        self.assertTrue(self.app.armed)

    def test_activity_dismisses_renderer(self):
        child = self.app.viewer = Mock()
        child.poll.return_value = None
        self.app.last_idle = 400
        self.app.poll()
        child.terminate.assert_called_once()

    def test_lock_dismisses_renderer(self):
        child = self.app.viewer = Mock()
        child.poll.return_value = None
        self.app.lock_changed(None, None, None, None, None, saver.GLib.Variant('(b)', (True,)))
        child.terminate.assert_called_once()

    def test_inhibitor_prevents_idle_activation(self):
        self.app.call.return_value = 400000
        self.app.bus.call_sync.return_value.unpack.return_value = (True,)
        with patch.object(saver.subprocess, 'Popen') as spawn:
            self.app.poll()
            spawn.assert_not_called()
            self.assertTrue(self.app.armed)

    def test_idle_activation_is_once_until_activity(self):
        self.app.call.return_value = 400000
        with patch.object(saver.subprocess, 'Popen') as spawn:
            spawn.return_value.poll.return_value = None
            self.app.poll()
            self.app.poll()
            spawn.assert_called_once()
            self.assertFalse(self.app.armed)

if __name__ == '__main__':
    unittest.main()
