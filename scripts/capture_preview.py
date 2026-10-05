#!/usr/bin/python3
"""Capture the real WebKit/ttfx animation — made by ycangignacy."""
from pathlib import Path
import functools
import http.server
import tempfile
import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, WebKit, GLib
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT/'app/web')))
threading.Thread(target=server.serve_forever, daemon=True).start()
app = Gtk.Application(application_id='local.fedora.screensaver.capture')
frames = []
folder = tempfile.TemporaryDirectory(prefix='fedora-preview-')
font = ImageFont.load_default(size=13)
def activate(app):
    win = Gtk.ApplicationWindow(application=app, title='Fedora Screensaver preview capture')
    win.set_default_size(960, 540)
    win.set_decorated(False)
    view = WebKit.WebView()
    win.set_child(view)
    view.load_uri(f'http://127.0.0.1:{server.server_port}/index.html?effect=beams&seed=24&capture=1')
    win.present()
    def next_frame():
        def advanced(view, result, *args):
            value = view.evaluate_javascript_finish(result).to_string()
            if value == 'waiting':
                GLib.timeout_add(100, lambda: next_frame() or False)
                return
            def snapshot(view, result, *args):
                file = Path(folder.name)/'frame.png'
                view.get_snapshot_finish(result).save_to_png(str(file))
                img = Image.open(file).convert('RGB').resize((640,360), Image.Resampling.LANCZOS)
                ImageDraw.Draw(img).text((14,335), 'made by ycangignacy', fill='#868d9e',font=font)
                frames.append(img.quantize(colors=32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE))
                if len(frames) < 100:
                    next_frame()
                else:
                    (ROOT/'docs').mkdir(exist_ok=True)
                    frames[0].save(ROOT/'docs/preview.gif',save_all=True,append_images=frames[1:],duration=100,loop=0,optimize=True)
                    frames[-1].save(ROOT/'docs/preview.png')
                    print('Captured',len(frames),'frames; engine:',value,flush=True)
                    app.quit()
            view.get_snapshot(WebKit.SnapshotRegion.VISIBLE,WebKit.SnapshotOptions.NONE,None,snapshot,None)
        view.evaluate_javascript('window.saver ? JSON.stringify(window.saver.step(12)) : "waiting"',-1,None,None,None,advanced,None)
    GLib.timeout_add(500,lambda:next_frame() or False)
app.connect('activate', activate)
app.run([])
folder.cleanup()
server.shutdown()
