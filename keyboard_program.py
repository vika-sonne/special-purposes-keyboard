#!/usr/bin/env python

from sys import argv, exit
from time import sleep
from usb.core import find, USBError
from configparser import ConfigParser
from re import match, compile, IGNORECASE
from argparse import ArgumentParser


DEFAULT_LAYOUT_FILEPATH = 'layout.ini'

# USB parameters
VENDOR, PRODUCT = 0x1189, 0x8890

# Programming sequences
START = '03000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000'
PREF = '03a10100 00000000 00000000 00000000 00000000 00000000 00000000 00000000'
# kcisc: key number, keys count, key sequence index, special keys (1 CTRL, 2 SHIFT, 4 ALT, 8 META/WIN), code (see SYMBOLS_CODES)
KEYkcisc = '03{:02X}11{:02X} {:02X}{:02X}{:02X}00 00000000 00000000 00000000 00000000 00000000 00000000'
# kbws: key number, mouse button (1 LEFT, 2 RIGHT, 4 MIDDLE), mouse weel (1 UP, 0xFF DOWN), special keys (1 CTRL, 2 SHIFT, 4 ALT)
MOUSEkbws = '03{:02X}13{:02X} 0000{:02X}{:02X} 00000000 00000000 00000000 00000000 00000000 00000000'
# kc: key number, code (see SPECIALS_CODES_12)
KEY12kc = '03{:02X}12{:02X} 00000000 00000000 00000000 00000000 00000000 00000000 00000000'
# m: mode (0, 1, 2)
LEDm = '03b018{:02X} 00000000 00000000 00000000 00000000 00000000 00000000 00000000'
POST = '03aaaa00 00000000 00000000 00000000 00000000 00000000 00000000 00000000'

# Keyboard parameters

KEYS_MAX_COUNT = 6

# Encoders K1, K2,.. key codes: left, right, press
ENCODERS_KEYS = (
	(
		0x0D,
		0x0F,
		0x0E,
	),
	(
		0x10,
		0x12,
		0x11,
	),
)

ENCODERS_KINDS = ('left', 'right', 'press')
ENCODERS_KINDS_MAX_LEN = max(len(x) for x in ENCODERS_KINDS)

def get_encoder_to_key(number: int, kind: int | str) -> int | None:
	'''
	number -:- 1.. encoder (knob) number
	kind   -:- encoder kind (0 or "left", 1 or "right", 2 or "press")
	'''
	if isinstance(kind, str):
		kind = kind.lower()
		if kind not in ENCODERS_KINDS:
			return None
		kind = ENCODERS_KINDS.index(kind)
	if 0 < number <= len(ENCODERS_KEYS):
		return ENCODERS_KEYS[number - 1][kind]
	return None


# Symbols codes (11): keyboard key symbol to code
SYMBOLS_CODES = {
	# first row with F keys
	'esc': 0x29,
	'f1': 0x3A,
	'f2': 0x3B,
	'f3': 0x3C,
	'f4': 0x3D,
	'f5': 0x3E,
	'f6': 0x3F,
	'f7': 0x40,
	'f8': 0x41,
	'f9': 0x42,
	'f10': 0x43,
	'f11': 0x44,
	'f12': 0x45,
	'f14': 0x69,
	'f15': 0x6A,
	'f16': 0x6B,
	'f17': 0x6C,
	'f18': 0x6D,
	'f19': 0x6E,
	'f20': 0x6F,
	'f21': 0x70,
	'f22': 0x71,
	'f23': 0x72,
	'f24': 0x73,
	'prtscn': 0x47,
	'scrolllock': 0x47,
	'pause': 0x48,
	# second row with numbers
	'tilda': 0x35,
	'1': 0x1E,
	'2': 0x1F,
	'3': 0x20,
	'4': 0x21,
	'5': 0x22,
	'6': 0x23,
	'7': 0x24,
	'8': 0x25,
	'9': 0x26,
	'0': 0x27,
	'-': 0x2D,
	'minus': 0x2D,
	'+': 0x2E,
	'plus': 0x2E,
	'backspace': 0x2A,
	# letter keys
	'a': 0x04,
	'b': 0x05,
	'c': 0x06,
	'd': 0x07,
	'e': 0x08,
	'f': 0x09,
	'g': 0x0A,
	'h': 0x0B,
	'i': 0x0C,
	'j': 0x0D,
	'k': 0x0E,
	'l': 0x0F,
	'm': 0x10,
	'n': 0x11,
	'o': 0x12,
	'p': 0x13,
	'q': 0x14,
	'r': 0x15,
	's': 0x16,
	't': 0x17,
	'u': 0x18,
	'v': 0x19,
	'w': 0x1A,
	'x': 0x1B,
	'y': 0x1C,
	'z': 0x1D,
	'space': 0x2C,
	# control keys of letter block
	'tab': 0x2B,
	'capslock': 0x39,
	'enter': 0x28,
	# other keys of letter block: 3+2+3
	'[{': 0x2F,
	']}': 0x30,
	'\|': 0x31,
	';:': 0x33,
	'bracket': 0x34,
	',<': 0x36,
	'.>': 0x37,
	'/?': 0x38,
	# edit & navigation keys block
	'ins': 0x49,
	'del': 0x4C,
	'home': 0x4A,
	'end': 0x4D,
	'pgup': 0x4B,
	'pgdn': 0x4E,
	# arrows block
	'->': 0x4F,
	'<-': 0x50,
	'arrowdn': 0x51,
	'arrowup': 0x52,
	# numpad block
	'numlock': 0x53,
	'numdiv': 0x54,
	'nummul': 0x55,
	'num-': 0x56,
	'num+': 0x57,
	'num.': 0x63,
	'menu': 0x65,
	'num1': 0x59,
	'num2': 0x5A,
	'num3': 0x5B,
	'num4': 0x5C,
	'num5': 0x5D,
	'num6': 0x5E,
	'num7': 0x5F,
	'num8': 0x60,
	'num9': 0x61,
	'num0': 0x62,
	# mouse
	'mouseleft': 0x01,
	'mouseright': 0x02,
	'mousemiddle': 0x04,
	'mouseweelup': 0x01,
	'mouseweeldn': 0xFF,
}

def get_symbol_code(symbol: str | None) -> int | None:
	'Gets code from keyboard symbol'
	if symbol is not None and (code := SYMBOLS_CODES.get(symbol.lower() if symbol else ' ')):
		return code
	print(f'! Unknown code for symbol "{symbol}", skip this programming')
	return None

def get_codes_and_special_keys(value: str) -> tuple[int | list[int], int] | None:
	'return ([code1, code2,..], special_keys) or None'

	def parse_special_key(value: str) -> int:
		match value.lower():
			case 'ctrl' | 'c': return 1
			case 'shift' | 's': return 2
			case 'alt' | 'a': return 4
			case 'meta' | 'win' | 'm' | 'w': return 8
			case _: return 0

	codes, special_keys_value = [], 0

	if (sequence := value.split(',')) and sequence[0]:
		if (special_keys := sequence[0].split('+')):
			if len(special_keys) > 2 and (not special_keys[-1] and not special_keys[-2]):  # spetial case: +
				special_keys[-2:] = '+'
			for special_key in special_keys[:-1]:
				if (buff := parse_special_key(special_key)):
					special_keys_value |= buff  # use bitwise operator to fix the multiple same special keys
				else:
					print(f'Can\'t parse special key: {special_key}')
					return None
			if (code := get_symbol_code(special_keys[-1])):
				codes.append(code)
			sequence = sequence[1:]

	for symbol in sequence:
		if symbol:
			if (code := get_symbol_code(symbol)):
				codes.append(code)

	if codes:
		return codes if len(codes) > 1 else codes[0], special_keys_value
	return codes, special_keys_value

def dump_special_keys(special_keys: int) -> str:
	ret = ''
	if special_keys & 1:
		ret += 'CTRL+'
	if special_keys & 2:
		ret += 'SHIFT+'
	if special_keys & 4:
		ret += 'ALT+'
	if special_keys & 8:
		ret += 'META+'
	return ret[:-1] if ret else 'none'


# Special codes (12): keyboard key symbol to code
SPECIALS_CODES_12 = {
	'play/pause': 0xcd,
	'play': 0xcd,
	'pause': 0xcd,
	'mute': 0xe2,
	'volume+': 0xe9,
	'volume-': 0xea,
	'nextsong': 0xb5,
	'prevsong': 0xb6,
}

def get_special_code_12(symbol: str | None) -> int | None:
	'Gets code from SPECIALS_CODES_12'
	if symbol is not None and (code := SPECIALS_CODES_12.get(symbol.lower())):
		return code
	return None


def bind_key_to_symbol_code(key: int, symbol_code: int | list[int], special_keys: int = 0):
	'''
	key          -:- 1..KEYS_MAX_COUNT
	symbol_code  -:- code or sequence: [code1, code2,..]
	special keys -:- 1 CTRL, 2 SHIFT, 4 ALT, 8 META/WIN
	'''
	if type(symbol_code) is int:
		symbol_code = (symbol_code,)
	key, special_keys = key & 0xFF, special_keys & 0xFF
	if verbose > 1:
		print(f'	Bind KEY{key:02} to codes={tuple(f"0x{x:02X}" for x in symbol_code)} mod={dump_special_keys(special_keys)}')
	if not dry:
		ep.write(bytearray.fromhex(PREF))
		ep.write(bytearray.fromhex(KEYkcisc.format(key, len(symbol_code), 0, special_keys, 0)))
		for i, code in enumerate(symbol_code):  # keys count
			ep.write(bytearray.fromhex(KEYkcisc.format(key, len(symbol_code), i + 1, special_keys, code & 0xFF)))
		ep.write(bytearray.fromhex(POST))

def bind_key_to_mouse(key: int, button: int, weel: int, special_keys: int = 0):
	'''
	key          -:- 1..KEYS_MAX_COUNT
	button       -:- 1 LEFT, 2 RIGHT, 4 MIDDLE
	weel         -:- 1 UP, 0xFF DOWN
	special keys -:- 1 CTRL, 2 SHIFT, 4 ALT, 8 META/WIN
	'''
	key, button, special_keys = key & 0xFF, button & 0xFF, special_keys & 0xFF
	if verbose > 1:
		print(f'	Bind KEY{key=} to mouse {button=} {weel=:02X} mod={special_keys=}')
	if not dry:
		ep.write(bytearray.fromhex(PREF))
		ep.write(bytearray.fromhex(MOUSEkbws.format(key, button, weel, special_keys)))
		ep.write(bytearray.fromhex(POST))

def bind_key(key: int, symbol_code: int | list[int], special_keys: int = 0):
	'''
	key          -:- 1..KEYS_MAX_COUNT
	symbol_code  -:- code or sequence: [code1, code2,..]
	special keys -:- 1 CTRL, 2 SHIFT, 4 ALT, 8 META/WIN
	'''
	if verbose > 1:
		if type(symbol_code) == int:
			print(f'Key {key:02} programming to code=0x{symbol_code:02X} mod={dump_special_keys(special_keys)}')
		else:
			print(f'Key {key:02} programming to codes={tuple(f"0x{x:02X}" for x in symbol_code)} mod={dump_special_keys(special_keys)}')
	if 0 < key <= KEYS_MAX_COUNT:
		bind_key_to_symbol_code(key, symbol_code, special_keys)
	else:
		print(f'Skip key programming. Key number out of range 1..{KEYS_MAX_COUNT}: {key}')

def bind_encoder(number: int, kind: int, symbol_code: int | list[int], special_keys: int = 0):
	if verbose > 1:
		print(f'Encoder {number} {ENCODERS_KINDS[kind]} programming')
	if (key := get_encoder_to_key(number, kind)):
		bind_key_to_symbol_code(key, symbol_code, special_keys)
	else:
		print(f'Skip encoder programming. Encoder number out of range 1..{len(ENCODERS_KEYS)}: {number}')

def bind_encoder_special_12(number: int, kind: str, code: int):
	if verbose > 1:
		print(f'Encoder {number} {kind} programming')
	if (key := get_encoder_to_key(number, kind)):
		bind_key_to_special_code_12(key, code)
	else:
		print(f'Skip encoder programming. Encoder number out of range 1..{len(ENCODERS_KEYS)}: {number}')

def bind_encoder_config_section(section: object, number: int):
	'bind encoder according to section of config file'

	def get_section_symbol_code(section: object, section_key: str) -> tuple[int | list[int], int] | None:
		'Gets code from section & key of config file'
		if (key_value := section.get(section_key)):
			if verbose:
				print(f'Encoder {number} {section_key:{ENCODERS_KINDS_MAX_LEN}} programming to "{key_value}"')
			if (code := get_special_code_12(key_value)):
				bind_encoder_special_12(number, section_key, code)
				return None
			return get_codes_and_special_keys(key_value)
		return None

	if (codes_and_special_keys := get_section_symbol_code(section, 'left')):
		bind_encoder(number, 0, codes_and_special_keys[0], codes_and_special_keys[1])
	if (codes_and_special_keys := get_section_symbol_code(section, 'right')):
		bind_encoder(number, 1, codes_and_special_keys[0], codes_and_special_keys[1])
	if (codes_and_special_keys := get_section_symbol_code(section, 'press')):
		bind_encoder(number, 2, codes_and_special_keys[0], codes_and_special_keys[1])

def bind_key_to_special_code_12(key: int, code: int):
	'''
	key          -:- 1..KEYS_MAX_COUNT
	symbol_code  -:- code
	'''
	key, code = key & 0xFF, code & 0xFF
	if verbose > 1:
		print(f'	Bind KEY{key:02} to special 12 code=0x{code:02X}')
	if not dry:
		ep.write(bytearray.fromhex(PREF))
		ep.write(bytearray.fromhex(KEY12kc.format(key, code)))
		ep.write(bytearray.fromhex(POST))

def bind_led(mode: int):
	'''
	set LEDmode

	mode         -:- 0..2
	'''
	if verbose > 0:
		print(f'Set LEDmode to {mode:02}')
	if not dry:
		ep.write(bytearray.fromhex(PREF))
		ep.write(bytearray.fromhex(LEDm.format(mode)))
		ep.write(bytearray.fromhex(POST))

# process command-line

def parse_args() -> object:
	parser = ArgumentParser(
		description='Programming utility of special purposes keyboard with encoders and keys.'
		, epilog=f'Special keys: CTRL, SHIFT, ALT, META or WIN. Example: "ctrl+shift+alt+meta+<-" or "c+s+a+m+<-". Example multi-key sequence: "a,b,c" or "c+s+a+m+a,b,c". Known special keyboard USB Vendor:Product: {VENDOR:02X}:{PRODUCT:02X}. Known symbols:\n{", ".join("{}".format(s) for s in SYMBOLS_CODES)}, {", ".join("{}".format(s) for s in SPECIALS_CODES_12)}')
	parser.add_argument('-l', '--layout', metavar='FILEPATH', default=DEFAULT_LAYOUT_FILEPATH, help=f'keyboard layout file path; default: {DEFAULT_LAYOUT_FILEPATH}')
	parser.add_argument('-d', '--dry', action='store_true', help=f'don\'t iteract with keyboard. Set this option to validate keyboard layout file')
	parser.add_argument('-v', '--verbose', '-v', action='count', default=0, help='verbose level; use multiple times to increase log level; example: -vv')
	return parser.parse_args()

args = parse_args()
layout_file_path, dry, verbose = args.layout, args.dry, args.verbose
if dry:
	print('DRY RUN !')

# read & parse layout config file
if verbose:
	print(f'Read layout config file "{layout_file_path}"')
config = ConfigParser()
try:
	if not config.read(layout_file_path):
		raise Exception('File not found')
except Exception as e:
	print(f'Error while read config file:\n{e}')
	exit(1)

if not dry:
	# wait for keybord attach
	while not (dev := find(idVendor=VENDOR, idProduct=PRODUCT)):
		sleep(1)

	if verbose:
		print('SPECIAL KEYBOARD CONNECTED')

	# get output USB endpoint
	try:
		cfg = dev.get_active_configuration()
	except USBError as e:
		if e.errno == 13:
			print('! Access to USB denied:')
			print(e)
			exit(e.errno)
		raise
	# print(f'{cfg=}')
	i = cfg.interfaces()[1]
	# print(f'{i=}')
	ep = i.endpoints()[0]
	# print(f'{ep=}')

	# prepare keyboard to programming & check USB connection
	try:
		ep.write(bytearray.fromhex(START))
	except USBError:
		print('Keyboard busy, abort')
		exit(2)

# programming encoders, keys & leds
re_encoder, re_keys, re_leds = compile('^K(\d)$', IGNORECASE), compile('^KEYS$', IGNORECASE), compile('^LED$', IGNORECASE)
for section in config:
	if (m := re_encoder.match(section)):
		# encoder section # get number of encoder and symbol codes to bind
		number, section = int(m[1]), config[section]
		bind_encoder_config_section(section, number)
	elif (m := re_keys.match(section)):
		# key section # get symbol codes to bind to key number
		section = config[section]
		for number, symbol in section.items():
			try:
				number = int(number)
			except ValueError:
				print(f'Wrong key number "{number}", skip this programming')
			else:
				if (code := get_special_code_12(symbol)):
					if verbose:
						print(f'Key {number:02} programming to "{symbol}"')
					bind_key_to_special_code_12(number, code)
				elif (codes_and_special_keys := get_codes_and_special_keys(symbol)) and codes_and_special_keys[0]:
					if verbose:
						print(f'Key {number:02} programming to "{symbol}"')
					bind_key(number, codes_and_special_keys[0], codes_and_special_keys[1])
	elif (m := re_leds.match(section)):
		# LED section # get mode
		section = config[section]
		for name, LEDmode in section.items():
			try:
				LEDmode = int(LEDmode)
			except ValueError:
				print(f'Wrong LED mode "{LEDmode}", skip this programming')
			else:
				if (name != "mode" or LEDmode not in range(3)):
					print(f'Wrong LED mode "{name} = {LEDmode}", skip this programming')
				else:
					bind_led (LEDmode)



if verbose:
	print('DONE')
