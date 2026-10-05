# Omarchy Screensaver for Fedora

**made by ycangignacy** · [English](../README.md)

Animowany napis **FEDORA** w stylu wygaszacza Omarchy. Aplikacja ma 37 efektów, działa bez Internetu i uruchamia wygaszacz na każdym monitorze po 5 minutach bezczynności.

![Animacja FEDORA — made by ycangignacy](preview.gif)

## Instalacja

Projekt jest przeznaczony dla **Fedory Workstation z GNOME**. Sprawdzono go na Fedorze 44, GNOME 50 i Waylandzie, na dwóch monitorach.

Zainstaluj potrzebne pakiety:

```bash
sudo dnf install git python3-gobject gtk4 webkitgtk6.0
```

Pobierz repozytorium i uruchom instalator:

```bash
git clone --branch v1.0.0 https://github.com/ycangignacy/omarchyscreensaverforfedora.git
cd omarchyscreensaverforfedora
./install.sh
```

Instalator uruchom **bez sudo**, w swojej sesji GNOME. Możesz też pobrać ZIP ze strony [wydania v1.0.0](https://github.com/ycangignacy/omarchyscreensaverforfedora/releases/tag/v1.0.0), rozpakować go i wykonać `./install.sh` w jego katalogu.

## Raz instalujesz — potem działa samo

Po instalacji, każdym restarcie komputera i zalogowaniu do GNOME wygaszacz uruchamia się **automatycznie po 5 minutach bezczynności**. Nie musisz otwierać aplikacji ani nic klikać. Autostart włącza się od razu — restart po instalacji nie jest potrzebny.

Aby animacja zastępowała systemowe wygaszanie i komputer nie przechodził automatycznie w uśpienie, zainstaluj ją tak:

```bash
./install.sh --replace-blanking --disable-suspend
```

To opcjonalna zmiana ustawień GNOME. **Super+L nadal pokazuje standardową blokadę z Twoją tapetą.**

## Uruchamianie

W menu aplikacji wyszukaj **Fedora Screensaver**. Możesz też wykonać:

```bash
~/.local/bin/fedora-screensaver
```

- **F** przełącza pełny ekran.
- **Esc** zamyka ręcznie otwarty podgląd.
- Wygaszacz po bezczynności zamyka się po ruchu myszy, kliknięciu albo naciśnięciu klawisza.
- **Super+L** pozostaje zwykłą blokadą GNOME z Twoją tapetą.

Animacja sama nie blokuje komputera. Domyślna instalacja zachowuje dotychczasowe ustawienia wygaszania, blokady i usypiania GNOME.

## Zastąp systemowe wygaszanie i wyłącz usypianie

Jeżeli animacja ma pozostać na ekranie zamiast systemowego wygaszania, użyj:

```bash
./install.sh --replace-blanking --disable-suspend
```

Pierwsza opcja wyłącza automatyczne wygaszanie, przyciemnianie i blokadę po bezczynności. Ręczna blokada **Super+L** nadal działa. Druga wyłącza automatyczne usypianie na zasilaczu i baterii. Możesz użyć tylko jednej z tych opcji.

Ustawienia zmienione przez instalator zostaną przywrócone podczas odinstalowania.

## Czas bezczynności

Domyślnie to 300 sekund, czyli 5 minut. Na przykład 10 minut ustawisz tak:

```bash
./install.sh --idle-seconds 600
```

Możesz też zmienić `idle_seconds` w `~/.local/share/fedora-ascii-screensaver/config.json`.

## Autostart

Wyłącz automatyczne uruchamianie:

```bash
systemctl --user disable --now fedora-ascii-screensaver.service
```

Włącz je ponownie:

```bash
systemctl --user enable --now fedora-ascii-screensaver.service
```

Sama aplikacja w menu pozostaje dostępna. Instalacja bez włączania autostartu: `./install.sh --no-autostart`.

## Aktualizacja i usunięcie

W katalogu repozytorium:

```bash
git fetch --tags
git checkout v1.0.0
./install.sh
```

Aktualizacja zachowuje ustawiony czas bezczynności. Aby odinstalować aplikację:

```bash
./uninstall.sh
```

Usuwane są pliki zarządzanej instalacji, skrót i usługa. Pobrane repozytorium pozostaje na dysku. Instalator nie nadpisuje nieznanej wcześniejszej instalacji — zatrzymuje się i pokazuje jej lokalizację.

## Gdy coś nie działa

```bash
systemctl --user status fedora-ascii-screensaver.service
journalctl --user -u fedora-ascii-screensaver.service -n 30
```

Sprawdź, czy pracujesz w GNOME, sesja nie jest zablokowana i monitor nie wyłącza się przed upływem 5 minut. Odtwarzacz filmów lub aplikacja prezentacyjna mogą wstrzymać wygaszacz.

## Autorzy

Aplikacja, instalator i integracja z Fedorą: **made by ycangignacy**.

Animacje pochodzą z [TerminalTextEffects](https://github.com/ChrisBuilds/terminaltexteffects) i jego portu [ttfx](https://github.com/omacom/ttfx). Pozostałe informacje o autorach i licencjach znajdziesz w [NOTICE](../NOTICE) i [licenses](../licenses/).
