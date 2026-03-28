# battery-monitor

windows said "10% battery remaining" and you didn't see it. again.

this app fixes that by going absolutely unhinged when your battery is low.

---

**what happens:**

your screen goes dark. your laptop beeps 3 times. then this takes over your entire screen:

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

you have 5 seconds to contemplate your choices. then it goes away.

---

**how to use:**

1. run `python battery_monitor/main.py`
2. battery icon shows up in your system tray
3. right-click to set your threshold (default: 20%)
4. forget it exists
5. get yelled at

---

**install deps:**
```bash
pip install -r requirements.txt
```

**or just grab the .exe from releases and double-click it.**

---

*[demo](https://x.com/shraddhaha/status/2036340751953698978)*
