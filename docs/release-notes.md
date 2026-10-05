# Fedora Screensaver v1.0.0

**made by ycangignacy**

The first stable release brings the Omarchy-style FEDORA animation to Fedora Workstation with GNOME. It includes 37 effects, a desktop launcher, a fullscreen preview and automatic startup after five minutes of inactivity on each monitor.

Download **omarchyscreensaverforfedora-v1.0.0.zip**, extract it and open a terminal in the extracted folder:

```bash
sudo dnf install python3-gobject gtk4 webkitgtk6.0
./install.sh
```

Run the installer without sudo. To replace automatic GNOME blanking and disable automatic suspend, use `./install.sh --replace-blanking --disable-suspend`. Super+L keeps the normal GNOME lock screen with your wallpaper. The animation itself does not lock your session.

[Installation guide and animated preview](https://github.com/ycangignacy/omarchyscreensaverforfedora/tree/v1.0.0) · [Polski poradnik](https://github.com/ycangignacy/omarchyscreensaverforfedora/blob/v1.0.0/docs/README.pl.md)

Tested on Fedora 44, GNOME 50 and Wayland with two monitors. Upstream licenses and credits are included in the package. SHA256SUMS is available to verify the ZIP download.
