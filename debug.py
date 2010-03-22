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


# Debug Mode Started -----------------------------------------------------------
# ------------------------------------------------------------------------------
import sys
import os

PATH = os.path.join(sys.path[0], "atarashii/usr/share/pyshared")


# Import Atarashii -------------------------------------------------------------
sys.path.insert(0, PATH)
try:
    import atarashii
    
except:
    if sys.path[0] == PATH: 
        sys.path.pop(0)
        
    sys.exit(os.EX_TEMPFAIL)

# Check what we should start ----------------------------------------------------
sys.path.pop(0)
arg = ""
if len(sys.argv) == 2:
    arg = sys.argv[1]

# Application
if arg == "main":
    atarashii.debug(sys.path[0])

# Crash Wrapper
else:
    if arg == "auto":
        import time
        time.sleep(3)
    
    # Wrap arround crazy random GDK and XOrg Erros ^.^"
    import subprocess
    restart_max = 2
    restart_count = 0
    while True:
        print "Starting Atarashii..."
        error = subprocess.call(["python", "debug.py", "main"])
        if error == os.EX_UNAVAILABLE:
            print "Atarashii is already running"
            break
        
        elif error == os.EX_TEMPFAIL:
            print "Importing Atarashii failed"
            break
        
        # 1 = ??, -9/-11 for kill and quit
        elif error in (os.EX_OK, 1, -9, -11): 
            print "Atarashii has been closed with status %d" % error
            break
        
        else:
            atarashii.crash(error)
            if restart_count >= restart_max:
                break
            
            restart_count += 1
            print "Atarashii crashed with %d! Restart #%d/%d" \
                   % (error, restart_count, restart_max) 
    
    exit(error)

