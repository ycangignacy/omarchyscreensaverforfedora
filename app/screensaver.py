#!/usr/bin/python3
"""Fedora Screensaver — made by ycangignacy."""
import argparse
import json
from pathlib import Path
import signal
import subprocess
import sys
import functools
import http.server
import threading
import time
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gdk, Gio, GLib, GLibUnix, Gtk, WebKit

ROOT = Path(__file__).resolve().parent

def config():
    return json.loads((ROOT / 'config.json').read_text())

class IdleMonitor(Gio.Application):
    """Keep idle detection separate from the disposable GTK/WebKit renderer."""
    def __init__(self):
        super().__init__(application_id='local.fedora.asciisaver', flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.viewer = None
        self.started = False
        self.armed = True
        self.last_idle = None
        self.connect('activate', self.activate)
        self.connect('shutdown', lambda *args: self.dismiss())

    def activate(self, app):
        if self.started:
            self.show()
            return
        self.started = True
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.hold()
        GLib.timeout_add(1000, self.poll)
        self.bus.signal_subscribe('org.gnome.ScreenSaver', 'org.gnome.ScreenSaver', 'ActiveChanged', '/org/gnome/ScreenSaver', None, Gio.DBusSignalFlags.NONE, self.lock_changed)

    def call(self, dest, path, iface, method):
        return self.bus.call_sync(dest, path, iface, method, None, None, Gio.DBusCallFlags.NONE, 1000, None).unpack()[0]

    def locked(self):
        return self.call('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver', 'org.gnome.ScreenSaver', 'GetActive')

    def poll(self):
        if self.viewer is not None and self.viewer.poll() is not None:
            self.viewer = None
        try:
            idle = self.call('org.gnome.Mutter.IdleMonitor', '/org/gnome/Mutter/IdleMonitor/Core', 'org.gnome.Mutter.IdleMonitor', 'GetIdletime') / 1000
            if self.viewer and self.last_idle is not None and idle + .15 < self.last_idle:
                self.dismiss()
            self.last_idle = idle
            if self.locked():
                self.dismiss()
            elif idle < 2:
                self.armed = True
            elif idle >= config()['idle_seconds'] and self.armed and not self.viewer:
                # Respect GNOME session inhibitors (movies/presentations).
                inhibited = self.bus.call_sync('org.gnome.SessionManager', '/org/gnome/SessionManager', 'org.gnome.SessionManager', 'IsInhibited', GLib.Variant('(u)', (8,)), None, Gio.DBusCallFlags.NONE, 1000, None).unpack()[0]
                if not inhibited:
                    self.armed = False
                    self.show()
        except GLib.Error as exc:
            print('Idle monitor:', exc, flush=True)
        return True

    def lock_changed(self, connection, sender, path, interface, signal_name, params):
        if params.unpack()[0]:
            self.dismiss()

    def show(self):
        if self.viewer is not None:
            if self.viewer.poll() is None:
                return
            self.viewer = None
        if self.locked():
            return
        self.viewer = subprocess.Popen([sys.executable, str(ROOT / 'screensaver.py')])
        self.last_idle = None

    def dismiss(self):
        viewer, self.viewer = self.viewer, None
        if viewer is None:
            return
        if viewer.poll() is None:
            viewer.terminate()
        try:
            viewer.wait(timeout=3)
        except subprocess.TimeoutExpired:
            viewer.kill()
            viewer.wait()


class Saver(Gtk.Application):
    def __init__(self, args):
        super().__init__(application_id='local.fedora.asciisaver.preview' if args.window else 'local.fedora.asciisaver.renderer', flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.args = args
        self.windows = []
        self.httpd = None
        self.started = 0
        self.armed = True
        self.last_idle = None
        self.connect('activate', self.activate)

    def activate(self, app):
        if self.started:
            self.show()
            return
        self.started = time.monotonic()
        self.bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)
        self.show()
        self.bus.signal_subscribe('org.gnome.ScreenSaver', 'org.gnome.ScreenSaver', 'ActiveChanged', '/org/gnome/ScreenSaver', None, Gio.DBusSignalFlags.NONE, self.lock_changed)
        if self.args.preview_seconds:
            GLib.timeout_add(int(self.args.preview_seconds*1000), self.finish_preview)

    def call(self, dest, path, iface, method):
        return self.bus.call_sync(dest, path, iface, method, None, None, Gio.DBusCallFlags.NONE, 1000, None).unpack()[0]

    def locked(self):
        return self.call('org.gnome.ScreenSaver', '/org/gnome/ScreenSaver', 'org.gnome.ScreenSaver', 'GetActive')

    def lock_changed(self, connection, sender, path, interface, signal_name, params):
        if params.unpack()[0]:
            self.dismiss()

    def show(self):
        if self.windows or self.locked():
            return
        if self.httpd is None:
            class Handler(http.server.SimpleHTTPRequestHandler):
                def log_message(self, *args):
                    pass
            handler = functools.partial(Handler, directory=str(ROOT / 'web'))
            self.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
            threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        self.started = time.monotonic()
        self.last_idle = None
        monitors = Gdk.Display.get_default().get_monitors()
        for i in range(monitors.get_n_items()):
            win = Gtk.ApplicationWindow(application=self, title='Fedora Screensaver — made by ycangignacy')
            win.set_decorated(self.args.window)
            win.set_cursor_from_name('none')
            area = WebKit.WebView()
            area.load_uri(f'http://127.0.0.1:{self.httpd.server_port}/index.html')
            win.set_child(area)
            keys = Gtk.EventControllerKey()
            keys.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
            keys.connect('key-pressed', self.key_pressed)
            win.add_controller(keys)
            click = Gtk.GestureClick()
            click.connect('pressed', lambda *a: None if self.args.window else self.dismiss())
            win.add_controller(click)
            motion = Gtk.EventControllerMotion()
            motion.connect('motion', self.motion)
            win.add_controller(motion)
            win.connect('close-request', lambda *a: self.dismiss() or True)
            self.windows.append(win)
            if self.args.window:
                win.set_default_size(1200, 760)
                win.maximize()
            else:
                win.fullscreen_on_monitor(monitors.get_item(i))
            win.present()
            if self.args.window:
                break

    def motion(self, *args):
        if not self.args.window and time.monotonic()-self.started > 1:
            self.dismiss()

    def key_pressed(self, controller, keyval, keycode, state):
        if self.args.window:
            if keyval in (Gdk.KEY_f, Gdk.KEY_F):
                win = self.windows[0]
                if win.is_fullscreen():
                    win.unfullscreen()
                else:
                    win.fullscreen()
                return True
            if keyval != Gdk.KEY_Escape:
                return False
        self.dismiss()
        return True

    def dismiss(self):
        windows, self.windows = self.windows, []
        for win in windows:
            win.destroy()
        self.quit()

    def finish_preview(self):
        self.quit()
        return False

def main():
    parser = argparse.ArgumentParser(description='Fedora Screensaver — made by ycangignacy')
    parser.add_argument('--version', action='version', version='Fedora Screensaver 1.0.1 — made by ycangignacy')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--daemon', action='store_true')
    parser.add_argument('--preview-seconds', type=float)
    modes.add_argument('--window', action='store_true')
    args = parser.parse_args()
    app = IdleMonitor() if args.daemon else Saver(args)
    GLibUnix.signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, lambda: app.quit() or False)
    app.run([])

if __name__ == '__main__':
    main()
