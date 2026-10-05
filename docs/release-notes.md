# Fedora Screensaver v1.0.1

**made by ycangignacy**

This maintenance release fixes excessive CPU usage after dismissing the fullscreen screensaver.

## Fixes

- Fix the idle screensaver process consuming an entire CPU core after its fullscreen windows were closed.
- Separate GNOME idle detection from the GTK/WebKit animation: the animation runs in a short-lived renderer process.
- End and reap the renderer when the animation closes, user activity resumes, the session locks or the service stops.
- Force-stop and reap an unresponsive renderer after a three-second shutdown timeout.
- Add regression tests for renderer cleanup, idle activation, locking and GNOME session inhibitors.

Resolution, animation timing and the 120-step-per-second animation setting are unchanged. No additional rendering optimization was applied.

## Verification

Tested again on the original Fedora 44 / GNOME 50 / Wayland PC with two monitors at 2560×1440 and 1920×1080:

- All 13 automated tests passed.
- All 37 animation effects passed an engine smoke test.
- Repeated fullscreen opening and closing left no animation processes running.
- The idle monitor measured approximately 0% CPU after dismissal, compared with approximately one full core before the fix.

**Po polsku:** naprawiono obciążenie całego rdzenia po zamknięciu wygaszacza. Animacja działa teraz w osobnym procesie, który jest kończony i sprzątany po zamknięciu, powrocie aktywności użytkownika lub blokadzie sesji. Rozdzielczość i tempo animacji pozostają bez zmian. Ponowne testy na komputerze użytkownika przeszły: 13 testów automatycznych oraz wszystkie 37 efektów.

## Installation and update

Download **omarchyscreensaverforfedora-v1.0.1.zip**, extract it and open a terminal in the extracted folder:

```bash
sudo dnf install python3-gobject gtk4 webkitgtk6.0
./install.sh
```

Run the installer without sudo. For an existing managed installation, rerun the installer from this version; it preserves the configured idle timeout.

**Install once, then it starts automatically.** After login to GNOME, the screensaver starts after five minutes of inactivity by default. No reboot is required.

To replace automatic GNOME blanking and disable automatic suspend, use:

```bash
./install.sh --replace-blanking --disable-suspend
```

Super+L keeps the normal GNOME lock screen with your wallpaper. The animation itself does not lock your session.

**Raz instalujesz — potem działa samo.** Domyślnie animacja pojawia się po pięciu minutach bezczynności. Instalator uruchom bez sudo; powyższe opcje zastępują systemowe wygaszanie i wyłączają automatyczne usypianie. Super+L zachowuje standardową blokadę.

[Installation guide and animated preview](https://github.com/ycangignacy/omarchyscreensaverforfedora/tree/v1.0.1) · [Polski poradnik](https://github.com/ycangignacy/omarchyscreensaverforfedora/blob/v1.0.1/docs/README.pl.md)

Upstream licenses and credits are included in the package. SHA256SUMS is available to verify the ZIP download.
