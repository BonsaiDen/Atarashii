import sys, os
sys.path.insert(0, os.path.join(sys.path[0], "atarashii/usr/share/pyshared"))
try:
	import atarashii

finally:
	sys.path.pop(0)
	
	
atarashii.debug(sys.path[0])
