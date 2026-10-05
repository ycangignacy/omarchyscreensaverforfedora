# Changelog

made by ycangignacy

## 1.0.1 — 2026-10-05

- Fix a full CPU core being consumed after dismissing the fullscreen screensaver.
- Run idle detection in a Gio application and animations in a short-lived GTK/WebKit process.
- Reap renderer processes after exit; terminate them when activity resumes, the session locks or the service stops.
- Add regression coverage for process cleanup, idle activation and session inhibitors.

## 1.0.0 — 2026-10-05

First stable release for Fedora Workstation with GNOME.

- FEDORA animation with 37 effects, available offline.
- Desktop launcher, fullscreen preview and support for multiple monitors.
- Automatic startup after five minutes of inactivity.
- User installer and uninstaller with optional GNOME blanking and suspend settings.
- Standard GNOME lock screen on Super+L.
- Animated preview and installation guides in English and Polish.

Tested on Fedora 44, GNOME 50 and Wayland with two monitors.
