#!/usr/bin/env python3

import winreg, os

def decode_str(digital_product_id):

	start = 52
	end = start + 15
	hexpid = digital_product_id[start:end+1]

	digits = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'M', 'P', 'Q', 'R', 'T', 'V', 'W', 'X', 'Y', '2', '3', '4', '6', '7', '8', '9']

	decode_length = 29
	decode_string_length = 15

	out = dict()

	for i in range(decode_length-1, -1, -1):
		if (i+1) % 6 == 0 :
			out[i] = "-"
		else:
			digit_map_index = 0
			for j in range(decode_string_length-1, -1, -1):
				bv = (digit_map_index << 8) | hexpid[j]
				hexpid[j] = bv//24
				digit_map_index = bv % 24
				out[i] = digits[digit_map_index]

	return out

# Useful for debugging: lists all values in an opened key (winreg.OpenKey(...))
def list_values(key):
	i = 0
	while True:
		try:
			name, value, t = winreg.EnumValue(key, i)
			print(f"{name} -> {value}")
			i+=1
		except OSError:
			break

# Retrieves value in target_key
def get_value(target_key, value, arch_keys):
	for arch_key in arch_keys:
		key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, target_key, 0, winreg.KEY_READ | arch_key)
		try:
			value, t = winreg.QueryValueEx(key, value)
			value = value.hex()
			break
		except:
			continue
	else:
		sys.exit(f"[-] Could not find {TARGET_VALUE} in the Windows Registry")

	return key, value


if __name__ == "__main__":

	TARGET_KEY = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"
	TARGET_VALUE = "DigitalProductId"

	# Take into account different architectures
	proc_arch = os.environ['PROCESSOR_ARCHITECTURE'].lower()
	proc_arch64 = os.environ['PROCESSOR_ARCHITEW6432'].lower()
	if proc_arch == 'x86' and not proc_arch64:
		arch_keys = {0}
	elif proc_arch == 'x86' or proc_arch == 'amd64':
		arch_keys = {winreg.KEY_WOW64_32KEY, winreg.KEY_WOW64_64KEY}
	else:
		sys.exit(f"[-] Unhandled arch: {proc_arch}")

	# Get DigitalProductId
	k, v = get_value(TARGET_KEY, TARGET_VALUE, arch_keys)

	# Convert into a string ("A4 00 00 ...") for debugging purposes
	digital_product_id = ""
	for i, c in enumerate(v.upper()):
		digital_product_id += c
		if (i+1)%2 == 0:
			digital_product_id += " "

	# SUBSTITUTE HERE YOUR EXTERNAL DigitalProductId
	# digital_product_id = ...

	# Split to parse more easily
	digital_product_id = [(int(x, 16)) for x in digital_product_id.rstrip().split(" ")]

	# Decode DigitalProductKey
	o = decode_str(digital_product_id)

	# Print appropiately
	for i in range(max(o.keys())+1):
		print(o[i], end="")
	print("")
