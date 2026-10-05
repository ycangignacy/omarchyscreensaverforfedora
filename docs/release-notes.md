# Fedora Screensaver v1.0.0

**made by ycangignacy**

The first stable release brings the Omarchy-style FEDORA animation to Fedora Workstation with GNOME. It includes 37 effects, a desktop launcher, a fullscreen preview and automatic startup after five minutes of inactivity on each monitor.

Download **omarchyscreensaverforfedora-v1.0.0.zip**, extract it and open a terminal in the extracted folder:

```bash
sudo dnf install python3-gobject gtk4 webkitgtk6.0
./install.sh
```

**Install once, then it starts automatically.** After every restart and login to GNOME, the screensaver appears after **5 minutes without keyboard or mouse activity**. No clicking or opening the app is needed. Autostart is enabled immediately; you do not need to reboot after installation.

For the animation to replace GNOME blanking and disable automatic suspend, run:

```bash
./install.sh --replace-blanking --disable-suspend
```

**Raz instalujesz — potem działa samo.** Po każdym restarcie i zalogowaniu do GNOME animacja pojawia się po **5 minutach bezczynności**, bez otwierania aplikacji. Powyższe opcje zastępują systemowe wygaszanie i wyłączają automatyczne usypianie. Super+L zachowuje standardową blokadę z tapetą.

Run the installer without sudo. To replace automatic GNOME blanking and disable automatic suspend, use `./install.sh --replace-blanking --disable-suspend`. Super+L keeps the normal GNOME lock screen with your wallpaper. The animation itself does not lock your session.

[Installation guide and animated preview](https://github.com/ycangignacy/omarchyscreensaverforfedora/tree/v1.0.0) · [Polski poradnik](https://github.com/ycangignacy/omarchyscreensaverforfedora/blob/v1.0.0/docs/README.pl.md)

Tested on Fedora 44, GNOME 50 and Wayland with two monitors. Upstream licenses and credits are included in the package. SHA256SUMS is available to verify the ZIP download.
