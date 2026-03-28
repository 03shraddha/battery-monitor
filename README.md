# 🔋 Battery Monitor

> **my laptop died mid-presentation. never again.**

---

## what is this

it's a little Windows app that lives in your system tray and **screams at you** when your battery is about to die.

not a gentle ping. not a tiny notification you'll ignore.

a full-screen red overlay that takes over your entire screen and goes **⚠ SYSTEM CRITICAL FAILURE ⚠** until you plug in your charger.

your laptop will beep. your screen will dim. you will plug in. i promise.

---

## why i built this

windows battery notifications are a joke.

you're in the zone, headphones on, the little % icon goes from 20 → 10 → dead. you didn't see it. now you're crawling under your desk looking for the charger in the dark.

i built this so that never happens again. to me. or you.

---

## what it does

1. **sits quietly in your tray** — you forget it exists (good)
2. **checks your battery every 30 seconds** — silently judging you
3. **when you drop below your threshold and you're unplugged** it goes full chaos mode:
   - dims your screen to near-black
   - beeps at you (3 times, aggressively)
   - shows a full-screen red "SYSTEM CRITICAL FAILURE" overlay with an **angry cat ASCII art** and a countdown timer
   - auto-dismisses after 5 seconds and restores your screen
4. **then cools down for 5 minutes** — won't spam you, don't worry

---

## the overlay (this is the fun part)

```
⚠ SYSTEM CRITICAL FAILURE ⚠

    /\_____/\
   /  o   o  \
  ( ==  ^  == )
   )         (
  (           )
 ( (  )   (  ) )
(__(__)___(__)__)

CHARGE YOUR BATTERY NOW!
```

full screen. bright red. you cannot click through it.

plug in or wait 5 seconds. those are your options.

---

## features

- **custom threshold** — set it to whatever % you want (default: 20%)
- **sound toggle** — turn off the beeps if you're in a meeting (or leave them on for chaos)
- **enable/disable** — master switch if you need to turn it off temporarily
- **auto-starts with Windows** — registers itself in registry on first launch, no setup needed
- **settings saved automatically** — changes persist across restarts
- **single .exe** — no Python needed, no installer, just run it

---

## install

### option 1: just run it (easiest)

grab the `.exe` from [releases](https://github.com/03shraddha/battery-monitor/releases), double-click, done.

it'll appear in your system tray. right-click to configure.

### option 2: run from source

```bash
# clone the repo
git clone https://github.com/03shraddha/battery-monitor.git
cd battery-monitor

# install dependencies
pip install -r requirements.txt

# run it
python battery_monitor/main.py
```

### option 3: build the .exe yourself

```bash
pip install pyinstaller
build.bat
# finds the exe at dist/battery_monitor.exe
```

---

## requirements

- Windows 10/11
- Python 3.7+ (only if running from source)
- That's it

---

## how to use

1. run the app — battery icon appears in your system tray
2. **right-click the tray icon** to:
   - set your battery threshold (default 20%)
   - toggle sound on/off
   - enable/disable monitoring
   - quit
3. forget it exists
4. get yelled at when your battery is low
5. plug in

---

## demo

> see it in action → [twitter demo](https://x.com/shraddhaha/status/2036340751953698978)

---

## tech stack

- **psutil** — reads battery status
- **pystray** — system tray icon
- **Pillow** — draws the tray icon
- **tkinter** — the scary red overlay
- **winsound** — the beeping
- **screen-brightness-control** — dims your screen
- **PyInstaller** — packages it into a single .exe

---

## settings file

stored at `%APPDATA%\BatteryMonitor\settings.json`

```json
{
  "threshold": 20,
  "sound_enabled": true,
  "enabled": true,
  "cooldown": 300
}
```

edit manually if you want, the app will pick up changes on next alert check.

---

## faq

**Q: will this slow down my computer?**
A: it sleeps for 30 seconds between checks. no.

**Q: can i change the cooldown time?**
A: yes, edit the settings.json directly. default is 300 seconds (5 min).

**Q: what if my screen brightness control doesn't work?**
A: it falls back to a dark tkinter overlay. you'll still get the effect.

**Q: why the angry cat?**
A: you need the energy. trust me.

---

## contributing

found a bug? have a feature idea? open an issue or PR.

future ideas i haven't built yet:
- different sounds at different battery levels
- color-coded tray icon (green → yellow → red)
- "test alert" button in the menu
- linux/mac support (maybe)

---

## license

MIT — do whatever you want with it.

---

*built because i was tired of my laptop dying. shared because you probably are too.*
