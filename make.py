import sys, os, shutil, subprocess, hashlib

def getFileMD5(file):
	f = open(file, "rb")
	md5 = hashlib.md5()
	while True:
		data = f.read(8192)
		if not data:
			break
			
		md5.update(data)
	
	f.close()
	return md5.hexdigest()

# Gather Information about the project
sys.path.insert(0, os.path.join(sys.path[0], "atarashii/usr/share/pyshared"))
try:
	import atarashii

finally:
	sys.path.pop(0)

# Create DEBIAN directory
debDir = os.path.join(sys.path[0], "atarashii/DEBIAN")
if not os.path.exists(debDir):
	os.mkdir(debDir)


print "\n---- Packing changelog ----"
log = os.path.join(sys.path[0], 'changelog')
man = os.path.join(sys.path[0], 'manpage')
print "Copying logs and manpage..."
log1 = os.path.join(sys.path[0], "atarashii/usr/share/doc/atarashii/changelog")
log2 = os.path.join(sys.path[0], "atarashii/usr/share/doc/atarashii/changelog.Debian")
man1 = os.path.join(sys.path[0], "atarashii/usr/share/man/man1/atarashii.1")
shutil.copyfile(log, log1)
shutil.copyfile(log, log2)
shutil.copyfile(man, man1)
print "Removing old logs and manpage..."
try:
	os.unlink(log1 + '.gz')
except:
	pass
try:
	os.unlink(log2 + '.gz')
except:
	pass
try:
	os.unlink(man1 + '.gz')
except:
	pass
print "Packing new logs and manpage..."
subprocess.call(["gzip", "--best", log1])
subprocess.call(["gzip", "--best", log2])
subprocess.call(["gzip", "--best", man1])

# Check all files
print "\n---- Cleaning up ----"
print "Checking files..."
m = open(os.path.join(sys.path[0], "atarashii/DEBIAN/md5sums"), "w")
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
			print "- deleting %s" % file
		
		else:
			size += os.stat(file).st_size
			cf = file[len(cur)-3:]
			m.write("%s  %s\n" % (getFileMD5(file), cf))


m.close()
print "\n---- Stats ----"
print "Current Version is %s" % atarashii.__version__
print "Complete size is %d KB" % (size / 1024)

# Pack changelog
print "\n---- Packaging ----"

# Write control file
print "Creating control file..."
c = open(os.path.join(sys.path[0], "atarashii/DEBIAN/control"), "w")

c.write("""Package: atarashii
Version: """ + atarashii.__version__ + """-1
Section: misc
Priority: optional
Architecture: all
Installed-Size: """ + str(size / 1024) + """
Depends: python (>= 2.6), python-webkit, python-gtk2, python-gconf, python-gobject, python-dbus, python-notify, mplayer-nogui
Maintainer: Ivo Wetzel <ivo.wetzel@googlemail.com>
Description: Twitter Client for the GNOME Desktop
 Atarashii(Japanese for "New") is a Twitter Client specifically designed for the 
 GNOME Desktop. It uses GTK+ and webkit to archive a slim and functional design.
 The code itself is written in Python and uses the corresponding Python bindings
 for the GTK+ libraries.
""")
c.close()


# Create package
print "Kittens are playing with the contents of your package..."
print "...I mean we're building it!"
subprocess.call(["fakeroot", "dpkg-deb", "--build", "atarashii"])
shutil.move(os.path.join(sys.path[0], "atarashii.deb"), os.path.join(sys.path[0], "atarashii_%s-1_all.deb" % atarashii.__version__))
print "Build complete!"


