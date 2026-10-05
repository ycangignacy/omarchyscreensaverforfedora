#!/usr/bin/python3
"""Fedora Screensaver installer — made by ycangignacy."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SOURCE = Path(__file__).resolve().parent
HOME = Path.home()
DATA = Path(os.environ.get('XDG_DATA_HOME', HOME / '.local/share'))
CONFIG = Path(os.environ.get('XDG_CONFIG_HOME', HOME / '.config'))
APP = DATA / 'fedora-ascii-screensaver'
UNIT = CONFIG / 'systemd/user/fedora-ascii-screensaver.service'
DESKTOP = DATA / 'applications/local.fedora.asciisaver.desktop'
BIN = HOME / '.local/bin/fedora-screensaver'
MARKER = APP / '.installed-by-ycangignacy'
STATE = APP / '.gnome-settings.json'

def run(*args):
    subprocess.run(args, check=True)

def settings_changes(args):
    changes = {}
    if args.replace_blanking:
        changes.update({
            ('org.gnome.desktop.session', 'idle-delay'): 'uint32 0',
            ('org.gnome.desktop.screensaver', 'idle-activation-enabled'): 'false',
            ('org.gnome.settings-daemon.plugins.power', 'idle-dim'): 'false',
        })
    if args.disable_suspend:
        for supply in ('ac', 'battery'):
            changes[('org.gnome.settings-daemon.plugins.power', f'sleep-inactive-{supply}-type')] = "'nothing'"
            changes[('org.gnome.settings-daemon.plugins.power', f'sleep-inactive-{supply}-timeout')] = '0'
    return changes

def apply_settings(args):
    from gi.repository import Gio, GLib
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    for (schema, key), value in settings_changes(args).items():
        settings = Gio.Settings.new(schema)
        entry = f'{schema}/{key}'
        if entry not in state:
            state[entry] = settings.get_value(key).print_(True)
        # Save recovery preferences before changing the desktop setting.
        STATE.write_text(json.dumps(state, indent=2) + '\n')
        if not settings.set_value(key, GLib.Variant.parse(None, value, None, None)):
            raise RuntimeError(f'{schema}/{key} is not writable')
    Gio.Settings.sync()

def uninstall():
    if not MARKER.exists():
        raise RuntimeError(f'No managed installation at {APP}; existing files were left alone.')
    run('systemctl', '--user', 'disable', '--now', UNIT.name)
    if STATE.exists():
        from gi.repository import Gio, GLib
        for entry, value in json.loads(STATE.read_text()).items():
            schema, key = entry.rsplit('/', 1)
            Gio.Settings.new(schema).set_value(key, GLib.Variant.parse(None, value, None, None))
        Gio.Settings.sync()
    for file in (UNIT, DESKTOP, BIN):
        file.unlink(missing_ok=True)
    shutil.rmtree(APP)
    run('systemctl', '--user', 'daemon-reload')
    print('Removed Fedora Screensaver. Any desktop settings changed by the installer were restored.')

def install(args):
    import gi
    gi.require_version('Gtk', '4.0')
    gi.require_version('WebKit', '6.0')
    from gi.repository import Gtk, WebKit  # noqa: F401
    if os.environ.get('XDG_CURRENT_DESKTOP') and 'GNOME' not in os.environ['XDG_CURRENT_DESKTOP']:
        raise RuntimeError('Automatic idle detection requires a GNOME desktop session.')
    if APP.exists() and not MARKER.exists():
        raise RuntimeError(f'{APP} already exists. Nothing was overwritten. Rename that installation before installing this package.')
    if not MARKER.exists():
        for file in (BIN, UNIT, DESKTOP):
            if file.exists():
                raise RuntimeError(f'{file} already exists. Nothing was overwritten.')
    if args.dry_run:
        print(f'Application: {APP}\nLauncher: {BIN}\nMenu entry: {DESKTOP}\nUser service: {UNIT}')
        print('Desktop changes:', settings_changes(args) or 'none')
        print('Dry run complete; no files or settings were changed.')
        return
    previous_config = json.loads((APP / 'config.json').read_text()) if (APP / 'config.json').exists() else {}
    shutil.copytree(SOURCE / 'app', APP, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copytree(SOURCE / 'licenses', APP / 'licenses', dirs_exist_ok=True)
    for name in ('LICENSE', 'NOTICE'):
        shutil.copy2(SOURCE / name, APP / name)
    cfg = json.loads((APP / 'config.json').read_text())
    cfg.update(previous_config)
    if args.idle_seconds is not None:
        cfg['idle_seconds'] = args.idle_seconds
    (APP / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    MARKER.write_text('made by ycangignacy\n')
    for file in (BIN, UNIT, DESKTOP):
        file.parent.mkdir(parents=True, exist_ok=True)
    BIN.write_text('#!/bin/sh\n# made by ycangignacy\nif [ "$#" -eq 0 ]; then set -- --window; fi\nexec /usr/bin/python3 "' + str(APP / 'screensaver.py') + '" "$@"\n')
    BIN.chmod(0o755)
    # systemd paths need their own quoting, rather than shell quoting.
    exe = str(APP / 'screensaver.py').replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%')
    UNIT.write_text('[Unit]\nDescription=Fedora Screensaver — made by ycangignacy\nAfter=graphical-session.target\nPartOf=graphical-session.target\n\n[Service]\nType=simple\nExecStart=/usr/bin/python3 "' + exe + '" --daemon\nRestart=on-failure\nRestartSec=5\n\n[Install]\nWantedBy=graphical-session.target\n')
    DESKTOP.write_text('[Desktop Entry]\nType=Application\nName=Fedora Screensaver\nComment=Omarchy-style FEDORA animation — made by ycangignacy\nExec="' + str(BIN) + '"\nIcon=' + str(APP / 'icon.svg') + '\nTerminal=false\nCategories=Utility;\nStartupNotify=false\n')
    apply_settings(args)
    run('systemctl', '--user', 'daemon-reload')
    if not args.no_autostart:
        run('systemctl', '--user', 'enable', '--now', UNIT.name)
        run('systemctl', '--user', 'restart', UNIT.name)
    print(f'Installed Fedora Screensaver — made by ycangignacy\nOpen it from the application menu, or run {BIN}\nIdle timeout: {cfg["idle_seconds"]} seconds.')

def main():
    parser = argparse.ArgumentParser(description='Fedora Screensaver — made by ycangignacy')
    parser.add_argument('--uninstall', action='store_true', help='remove the managed installation and restore its desktop settings')
    parser.add_argument('--dry-run', action='store_true', help='check dependencies and show paths without changing anything')
    parser.add_argument('--no-autostart', action='store_true', help='install without starting or enabling the user service')
    parser.add_argument('--replace-blanking', action='store_true', help='disable GNOME automatic blanking, dimming and idle locking; manual lock remains available')
    parser.add_argument('--disable-suspend', action='store_true', help='disable automatic suspend on AC and battery power')
    parser.add_argument('--idle-seconds', type=int, help='idle timeout; default 300 for a new installation')
    args = parser.parse_args()
    if args.idle_seconds is not None and args.idle_seconds < 10:
        parser.error('--idle-seconds must be at least 10')
    if os.geteuid() == 0:
        parser.error('Run this installer as your desktop user, without sudo.')
    if args.uninstall and args.dry_run:
        print(f'Would uninstall {APP}; no changes made.')
        return
    try:
        uninstall() if args.uninstall else install(args)
    except (ImportError, ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'{exc}\nInstall dependencies with: sudo dnf install python3-gobject gtk4 webkitgtk6.0\n')

if __name__ == '__main__':
    main()
