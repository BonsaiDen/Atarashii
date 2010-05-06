Atarashii
=========

**Atarashii** is a simple Twitter Client for your GNOME Desktop.

| **Features include:**
| A clean minimalistic GUI, Desktop notifications with configurable sounds, 
| Themes, auto completion of usernames and CloudSync of read Tweets and 
| Messages.

It's build using *Python*, *GTK+* and *Webkit*.

Installation
------------

You can download the Debian-Package_ or clone the repository and build 
Atarashii yourself by opening a shell and issueing the following commands::

    git clone git://github.com/BonsaiDen/Atarashii.git
    cd Atarashii
    ./make

Now install the Debian-Package that was just created.  
If you just want to start Atarashii without installing it first just run ``./debug.py``.

    You may need to install ``fakeroot`` in order to be able to build the 
    package.  
    Also there is a rare bug where dpkg-deb fails to open/find the control file.  
    If you encounter this please send me a mail with more details.  

.. _Debian-Package: http://github.com/downloads/BonsaiDen/Atarashii/atarashii_0.99.28-1_all.deb

Contributing
------------

The source is available on GitHub_, to
contribute to the project, fork it on GitHub and send a pull request.
Everyone is welcome to make improvements to **Atarashii**!

.. _GitHub: http://github.com/BonsaiDen/Atarashii

License
=======

Copyright (c) 2010 Ivo Wetzel

**Atarashii** is free software: you can redistribute it and/or 
modify it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

**Atarashii** is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
**Atarashii**. If not, see <http://www.gnu.org/licenses/>.

