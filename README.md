# special-purposes-keyboard
**:snake: Python 3 CLI utility to programming special purposes keyboard**
_____________________________________________________

## This is an multi-OS implementation of programming a special purposes keyboard:
![](/media/640x640.jpg_.webp)

## Usage scenario

- Edit layout file.
- Program special purposes keyboard by this utility with command-line interface.

## Advantages of this utility
- You may have several layout files.
- Not need to use GUI to program and even for edit layout file (Unix way :robot:).
- Multy-OS usage. Feel free. :cowboy_hat_face:

# Layout file

Key programming pattern:

`key=symbol`

  where:

`key` - special purposes keyboard key;

`symbol` - action to do.

 ### Symbols examples:
 ```
 multi-key sequence: a,b,c
 with special keys: ctrl+shift+alt+meta+a
 the same: c+s+a+m+a
 multi-key sequence: c+s+a+m+a,b,c
```
 For knob programming use section with name `Kn` for knob `n`. Example:
 ```
[K1]
left=<-
right=->
press=enter
```
 For keys programming use KEYS section. Example:
```
[KEYS]
1=a
2=s+b
3=a+s+c,d,e
```
Available knobs and keys depends of special purposes keyboard model.

See layout file complete example: [layout.ini](/layout.ini).

# Programming
Be aware that USB subsystem access needs relevant rights. `sudo` for Kubuntu.

## Install Python requirements before usage:
```
pip install -r requirements.txt
```

## Command line help:
```
python3 ./keyboard_program.py -h
usage: keyboard_program.py [-h] [-l FILEPATH] [-d] [-v]

Programming utility of special purposes keyboard with encoders and keys.

options:
  -h, --help            show this help message and exit
  -l FILEPATH, --layout FILEPATH
                        keyboard layout file path; default: layout.ini
  -d, --dry             don't iteract with keyboard. Set this option to validate keyboard layout file
  -v, --verbose, -v     verbose level; use multiple times to increase log level; example: -vv

Special keys: CTRL, SHIFT, ALT, META or WIN. Example: "ctrl+shift+alt+meta+<-" or "c+s+a+m+<-". Example multi-key sequence: "a,b,c" or "c+s+a+m+a,b,c". Known special keyboard USB Vendor:Product: 1189:8890. Known symbols: esc, f1, f2,
f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, prtscn, scrolllock, pause, tilda, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, -, minus, +, plus, backspace, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z, [_], tab, capslock,
enter, [{, ]}, \|, ;:, '", ,<, .>, /?, ins, del, home, end, pgup, pgdn, ->, <-, arrowdn, arrowup, numlock, numdiv, nummul, num-, num+, num., menu, num1, num2, num3, num4, num5, num6, num7, num8, num9, num0, mouseleft, mouseright,
mousemiddle, mouseweelup, mouseweeldn
```
## Check layout file layout.ini:
```
sudo python3 ./keyboard_program.py -l "layout.ini" -vd
DRY RUN !
Read layout config file "layout.ini"
Encoder 1 left  programming to "<-"
Encoder 1 right programming to "->"
Encoder 1 press programming to "enter"
Key 03 programming to "3"
Key 02 programming to "2"
Key 01 programming to "1"
Key 06 programming to "6"
Key 05 programming to "5"
Key 04 programming to "4"
DONE
```

## Command line programming example with verbose output (use default layout file name layout.ini):
```
sudo python3 ./keyboard_program.py -v
Read layout config file "layout.ini"
SPECIAL KEYBOARD CONNECTED
Encoder 1 left  programming to "<-"
Encoder 1 right programming to "->"
Encoder 1 press programming to "enter"
Key 03 programming to "3"
Key 02 programming to "2"
Key 01 programming to "1"
Key 06 programming to "6"
Key 05 programming to "5"
Key 04 programming to "4"
DONE
```

## Command line programming example with more verbose output (use default layout file name layout.ini):
```
sudo python3 ./keyboard_program.py -vv
Read layout config file "layout.ini"
SPECIAL KEYBOARD CONNECTED
Encoder 1 left  programming to "<-"
Encoder 1 left  programming
        Bind KEY13 to codes=('0x50',) mod=none
Encoder 1 right programming to "->"
Encoder 1 right programming
        Bind KEY15 to codes=('0x4F',) mod=none
Encoder 1 press programming to "enter"
Encoder 1 press programming
        Bind KEY14 to codes=('0x28',) mod=none
Key 03 programming to "3"
Key 03 programming to code=0x20 mod=none
        Bind KEY03 to codes=('0x20',) mod=none
Key 02 programming to "2"
Key 02 programming to code=0x1F mod=none
        Bind KEY02 to codes=('0x1F',) mod=none
Key 01 programming to "1"
Key 01 programming to code=0x1E mod=none
        Bind KEY01 to codes=('0x1E',) mod=none
Key 06 programming to "6"
Key 06 programming to code=0x23 mod=none
        Bind KEY06 to codes=('0x23',) mod=none
Key 05 programming to "5"
Key 05 programming to code=0x22 mod=none
        Bind KEY05 to codes=('0x22',) mod=none
Key 04 programming to "4"
Key 04 programming to code=0x21 mod=none
        Bind KEY04 to codes=('0x21',) mod=none
DONE
```
