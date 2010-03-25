#!/usr/bin/python
#  This file is part of Atarashii.
#
#  Atarashii is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Debian Packager Creator ------------------------------------------------------
# ------------------------------------------------------------------------------
import sys, os, shutil, subprocess, hashlib, time

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


# Get latest commit number -----------------------------------------------------
print 'Saving commit count...'
proc = subprocess.Popen('git shortlog -s -n', shell = True, stdout = subprocess.PIPE)
stdout_value = proc.communicate()[0]
commit_count = 0
lines = stdout_value.split('\n')
for i in lines:
    e = i.split('\t')[0].strip()
    if e != '':
        commit_count += int(e)


init_file = os.path.join(sys.path[0], "atarashii/usr/share/pyshared/atarashii/__init__.py")
import re
countRegex = re.compile('__commits__ = \'([0-9]+)\'''')
f = open(init_file, 'rb')
init_data = f.read()
f.close()
init_data = countRegex.sub("__commits__ = '%s'" % commit_count, init_data)

f = open(init_file, 'wb')
f.write(init_data)
f.close()

# Gather Information about the project -----------------------------------------
sys.path.insert(0, os.path.join(sys.path[0], "atarashii/usr/share/pyshared"))
try:
    import atarashii

finally:
    sys.path.pop(0)


# Create DEBIAN directory ------------------------------------------------------
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
man2 = os.path.join(sys.path[0], "atarashii/usr/share/man/man1/atarashiigui.1")
shutil.copyfile(log, log1)
shutil.copyfile(log, log2)
shutil.copyfile(man, man1)
shutil.copyfile(man, man2)
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
try:
    os.unlink(man2 + '.gz')
except:
    pass
print "Packing new logs and manpage..."
subprocess.call(["gzip", "--best", log1])
subprocess.call(["gzip", "--best", log2])
subprocess.call(["gzip", "--best", man1])
subprocess.call(["gzip", "--best", man2])


# Check all files --------------------------------------------------------------
print "\n---- Cleaning up ----"
print "Checking files..."
m = open(os.path.join(sys.path[0], "atarashii/DEBIAN/md5sums"), "w")
size = 0
cur = os.path.join(sys.path[0], "atarashii/usr")
dirs = os.walk(cur)
tempFiles = []
for i in dirs:
    files = i[2]
    path = os.path.join(cur, i[0])
    subprocess.call(["chmod", "755", path])
    for f in files:
        file = os.path.join(path, f)
        if f.startswith('.'):
            print "- temping %s" % file
            to = os.path.join(sys.path[0], 'tmp' + f)
            tempFiles.append((file, to))
            shutil.move(file, to)
        
        elif f.endswith("~") or f.endswith(".pyc"):
            os.remove(file)
            print "- deleting %s" % file
        
        else:
            if f == "atarashii" or f == "atarashiigui":
                subprocess.call(["chmod", "644", file])
                subprocess.call(["chmod", "+x", file])
            else:
                subprocess.call(["chmod", "644", file])
            
            size += os.stat(file).st_size
            cf = file[len(cur)-3:]
            m.write("%s  %s\n" % (getFileMD5(file), cf))


m.close()
print "\n---- Stats ----"
print "Current Version is %s-%s" % (atarashii.__version__, commit_count)
print "Complete size is %d KB" % (size / 1024)


print "\n---- Packaging ----"


# Write control file -----------------------------------------------------------
print "Creating control file..."
try:
    os.remove(os.path.join(sys.path[0], "atarashii/DEBIAN/postinst~"))
    
except:
    pass

try:
    os.remove(os.path.join(sys.path[0], "atarashii/DEBIAN/postrm~"))
except:
    pass

c = open(os.path.join(sys.path[0], "atarashii/DEBIAN/control"), "w")

c.write("""Package: atarashii
Version: """ + atarashii.__version__ + """-1
Section: misc
Priority: optional
Architecture: all
Installed-Size: """ + str(size / 1024) + """
Depends: python (>= 2.6), python-webkit, python-gtk2, python-gconf, python-gobject, python-dbus, python-gnome2, libnotify1, libnotify-bin, mplayer-nogui
Maintainer: Ivo Wetzel <ivo.wetzel@googlemail.com>
Homepage: http://github.com/BonsaiDen/Atarashii
Description: Twitter Client for the GNOME Desktop
 Atarashii is a Twitter Client specifically designed for the 
 GNOME Desktop. It uses GTK+ and webkit to archive a slim and functional design.
 The code itself is written in Python and uses the corresponding Python bindings
 for the GTK+ libraries.
""")
c.close()
print ">> Created!"
time.sleep(0.1) # make sure dpkg-deb finds the control file!
print ""
# Create package
print "The kittens are building your package..."
dpkg = False
try:
    code = subprocess.call(["fakeroot", "dpkg-deb", "--build", "atarashii"], 
                    stdout = open("/dev/null", "wb"))
    if code == 0:         
        dkpg = True
    
    else:
        raise OSError, "DPKG failed"
    
    debfile = os.path.join(sys.path[0], "atarashii_%s-1_all.deb" % atarashii.__version__)
    shutil.move(os.path.join(sys.path[0], "atarashii.deb"), debfile)
    deb_size = os.stat(debfile).st_size / 1024



except OSError, error:
    if not dpkg:
        print """ERROR: Could not build Atarashii package due to missing 'fakeroot'.\n       Please install 'fakeroot' via the package manager and try again."""
    
    else:
        print """ERROR: dpkg-deb failed to create the package."""
        print error
    
    # Move all those temp files back
    for file, to in tempFiles:
        shutil.move(to, file)
    
    exit()

print ">> Build complete!"
print ">> Compressed size %d KB" % deb_size

# Move all those temp files back
for file, to in tempFiles:
    shutil.move(to, file)

# Check for errors
try:
    subprocess.call(["lintian"], stdout = open("/dev/null", "wb")) 
except:
    exit()

print "\n---- Checking for Errors ----"
subprocess.call(["lintian", "atarashii_%s-1_all.deb" % atarashii.__version__])
print ">> Done!"


