# battery-monitor

**[watch the demo →](https://x.com/shraddhaha/status/2036340751953698978/video/1)**

made this so my laptop yells at me if I forget to charge it

---

**what it does:**

sits in your system tray doing nothing. the moment your battery drops below your threshold and you're not plugged in — your screen dims, your laptop beeps, and a big red fullscreen warning shows up until you plug in.

it goes away on its own after 5 seconds. you don't have to do anything.

---

**to run it:**

```bash
pip install -r requirements.txt
python battery_monitor/main.py
```

or grab the `.exe` from releases and just double-click it.

right-click the tray icon to change the threshold (default is 20%).
