import sys, os, shutil, subprocess

# Gather Information about the project
sys.path.insert(0, os.path.join(sys.path[0], "atarashii/usr/share/pyshared"))
try:
	import atarashii

finally:
	sys.path.pop(0)
	
size = 0
cur = os.path.join(sys.path[0], "atarashii/usr")
dirs = os.walk(cur)
for i in dirs:
	files = i[2]
	path = os.path.join(cur, i[0])
	for f in files:
		file = os.path.join(path, f)
		if f.endswith("~") or f.endswith(".pyc"):
			os.remove(file)
			print "deleting %s" % file
		
		else:
			size += os.stat(file).st_size

print "Current Version is %s" % atarashii.__version__
print "Complete size is %d KB" % (size / 1024)

# Write control file
c = open(os.path.join(sys.path[0], "atarashii/DEBIAN/control"), "w")

c.write("""Package: atarashii
Version: """ + atarashii.__version__ + """-1
Section: misc
Priority: optional
Architecture: all
Installed-Size: """ + str(size / 1024) + """
Depends: python, python-webkit, python-gtk2, python-glade2, python-gconf, python-gobject, python-dbus, python-notify, mplayer-nogui, python-gnome2-desktop
Maintainer: Ivo Wetzel <ivo.wetzel@googlemail.com>
Description: Twitter Client for the GNOME Desktop
 Atarashii(Japanese for "New") is a Twitter Client specificly designed for the 
 GNOME Desktop. It uses GTK+ and webkit to archive a slim and functional design.
 The code itself is written in Python and uses the corresponding Python bindings
 for the GTK+ libraries.
""")
c.close()


# Create package
print "Building package..."
subprocess.call(["fakeroot", "dpkg-deb", "--build", "atarashii"])
shutil.move(os.path.join(sys.path[0], "atarashii.deb"), os.path.join(sys.path[0], "atarashii_%s-1_all.deb" % atarashii.__version__))
print "Build complete!"


