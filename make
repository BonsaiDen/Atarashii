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

def getStringMD5(string):
    md5 = hashlib.md5()
    md5.update(string)
    return md5.hexdigest()

def update_init_file(commits, sha):
    init_file = os.path.join(sys.path[0], "atarashii/usr/share/pyshared/atarashii/__init__.py")
    import re
    f = open(init_file, 'rb')
    init_data = f.read()
    f.close()
    countRegex = re.compile('__kittens__ = \'([0-9]+)\'''')
    init_data = countRegex.sub("__kittens__ = '%s'" % commits, init_data)
    shaRegex = re.compile('__secret__ = \'([0-9a-zA-Z]+)\'''')
    init_data = shaRegex.sub("__secret__ = '%s'" % sha, init_data)
    f = open(init_file, 'wb')
    f.write(init_data)
    f.close()


# Get latest commit number -----------------------------------------------------
print "\n-- Kittens are inspecting your repository " + '-' * 37
proc = subprocess.Popen('git shortlog -s -n', shell = True, stdout = subprocess.PIPE)
stdout_value = proc.communicate()[0]
commit_count = 0
lines = stdout_value.split('\n')
for i in lines:
    e = i.split('\t')[0].strip()
    if e != '':
        commit_count += int(e)

proc = subprocess.Popen('git log --shortstat -n 1', shell = True, stdout = subprocess.PIPE)
stdout_value = proc.communicate()[0]
commit_sha = stdout_value[7:14]

update_init_file(commit_count, commit_sha)

print ' ' + getStringMD5(str(commit_count))
print ' ' + getStringMD5(str(commit_sha))
print " = Done!"

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

print "\n-- Kittens are writing your changelogs " + '-' * 40
log = os.path.join(sys.path[0], 'changelog')
man = os.path.join(sys.path[0], 'manpage')
print ' ' + getStringMD5("Copying logs and manpage...")
log1 = os.path.join(sys.path[0], "atarashii/usr/share/doc/atarashii/changelog")
log2 = os.path.join(sys.path[0], "atarashii/usr/share/doc/atarashii/changelog.Debian")
man1 = os.path.join(sys.path[0], "atarashii/usr/share/man/man1/atarashii.1")
man2 = os.path.join(sys.path[0], "atarashii/usr/share/man/man1/atarashiigui.1")
shutil.copyfile(log, log1)
shutil.copyfile(log, log2)
shutil.copyfile(man, man1)
shutil.copyfile(man, man2)
print ' ' + getStringMD5("Removing old logs and manpage...")
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
print ' ' + getStringMD5("Packing new logs and manpage...")
subprocess.call(["gzip", "--best", log1])
subprocess.call(["gzip", "--best", log2])
subprocess.call(["gzip", "--best", man1])
subprocess.call(["gzip", "--best", man2])
print " = Done!"


# Check all files --------------------------------------------------------------
print "\n-- Kittens are calculating stuff, so you don't have to " + '-' * 24
m = open(os.path.join(sys.path[0], "atarashii/DEBIAN/md5sums"), "w")
size = 0
cur = os.path.join(sys.path[0], "atarashii/usr")
dirs = os.walk(cur)
tempFiles = []
deleted_count = 0
temped_count = 0
hashed_count = 0
for i in dirs:
    files = i[2]
    path = os.path.join(cur, i[0])
    subprocess.call(["chmod", "755", path])
    for f in files:
        file = os.path.join(path, f)
        if f.startswith('.'):
        #    print "- temping %s" % file
            temped_count += 1
            to = os.path.join(sys.path[0], 'tmp' + f)
            tempFiles.append((file, to))
            shutil.move(file, to)
        
        elif f.endswith("~") or f.endswith(".pyc"):
            os.remove(file)
            deleted_count += 1
           # print "- deleting %s" % file
        
        else:
            if f == "atarashii" or f == "atarashiigui":
                subprocess.call(["chmod", "644", file])
                subprocess.call(["chmod", "+x", file])
            
            else:
                subprocess.call(["chmod", "644", file])
            
            hashed_count += 1
            size += os.stat(file).st_size
            cf = file[len(cur)-3:]
            m.write("%s  %s\n" % (getFileMD5(file), cf))

m.close()
print ' ' + getStringMD5(str(temped_count))
print ' ' + getStringMD5(str(deleted_count))
print ' ' + getStringMD5(str(hashed_count))
cc = commit_count // 3.4
cd = int(commit_count * 5.7)
ce = cd // cc
tt = int(temped_count * ce)
result = (cc * cd) / (temped_count ** hashed_count ^ deleted_count * tt)

print ' = (%d * %d) / (%d ** %d ^ %d * %d) = %d' % (cc, cd, temped_count, hashed_count, deleted_count,  tt, result)

print "\n-- Kittens are building your package " + '-' * 42

# Write control file -----------------------------------------------------------
try:
    os.remove(os.path.join(sys.path[0], "atarashii/DEBIAN/postinst~"))
    
except:
    pass

try:
    os.remove(os.path.join(sys.path[0], "atarashii/DEBIAN/postrm~"))
except:
    pass

control_file = os.path.join(sys.path[0], "atarashii/DEBIAN/control")
c = open(control_file, "w")

c.write("""Package: atarashii
Version: """ + atarashii.__version__ + """-1
Section: misc
Priority: optional
Architecture: all
Installed-Size: """ + str(size / 1024) + """
Depends: python (>= 2.6), python-webkit, python-gtk2, python-gobject, python-dbus, python-gnome2, python-gconf, sox
Maintainer: Ivo Wetzel <ivo.wetzel@googlemail.com>
Homepage: http://github.com/BonsaiDen/Atarashii
Description: Twitter Client for the GNOME Desktop
 Atarashii is a Twitter Client specifically designed for the 
 GNOME Desktop. It uses GTK+ and webkit to archive a slim and functional design.
 The code itself is written in Python and uses the corresponding Python bindings
 for the GTK+ libraries.
""")
c.close()
time.sleep(0.1) # make sure dpkg-deb finds the control file!

# Create package
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
        print """  ERROR: Could not build Atarashii package due to missing 'fakeroot'.\n       Please install 'fakeroot' via the package manager and try again."""
    
    else:
        print """  ERROR: dpkg-deb failed to create the package."""
        print error
    
    # Move all those temp files back
    for file, to in tempFiles:
        shutil.move(to, file)
    
    update_init_file(0, "0000000")
    exit()

print ' ' + getFileMD5(control_file)
print ' ' + getFileMD5(debfile)
print " = Done!"

# Move all those temp files back
for file, to in tempFiles:
    shutil.move(to, file)

update_init_file(0, "0000000")

# Check for errors
try:
    subprocess.call(["lintian"], stdout = open("/dev/null", "wb")) 
    print "\n-- Kittens are checking for package errors " + '-' * 36
    subprocess.call(["lintian", "atarashii_%s-1_all.deb" % atarashii.__version__])
    print " = Done!"

except:
    pass

# Stats
print "\n-- Kittens are showing you some stats " + '-' * 41
print " Version: %s" % atarashii.__version__
print ' Kittens: %d' % commit_count
print '   Lucky: %s' % commit_sha
print "    Size: %d KB" % (size / 1024)
print " Compres: %d KB\n" % deb_size

