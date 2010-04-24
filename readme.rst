Atarashii
=========

**Atarashii** is a simple Twitter Client for your GNOME Desktop.

| **Features include:**
| A clean minimalistic GUI, Desktop notifications with configurable sounds,
| the possibility to theme the timeline and auto completion of usernames.

It's build using *Python*, *GTK+* and *Webkit*.


Installation
------------
There are currently three ways for you to get **Atarashii**.

**#1: Way of the user - Using the pre build Package**

This is most likely the simpelst one is to install the pre build Debian-Package_ 
from the Downloads section.

The package will automatically setup the repo config and install the public 
key, so you don't have to check for updates on GitHub, instead just use your
systems update manager.

**#2: GIT lovers choice - Installation from the repository**  

Open a shell and issue the following commands::

    git clone git://github.com/BonsaiDen/Atarashii.git
    ./make

After that just install the created Debian-Package.

    You may need to install ``fakeroot`` in order to be able to build the 
    package.
    Also there is a rare bug where dpkg-deb fails to open/find the control file.
    If you encounter this please send me a mail with more details.


**#3: For the real Coding Kittens - Running the debug version**

If you want to hack on **Atarashii** you can just clone the repo and then run 
``./debug`` to start Atarashii.

    Watch out if you clone the ``next`` branch, sometimes changes that get 
    pushed up their can break stuff.

.. _Debian-Package: http://github.com/downloads/BonsaiDen/Atarashii/atarashii_0.99.24-1_all.deb


TODO
----

- Add more translations ( See Issue6_ )
- Implement a search view(?)

.. _Issue6: http://github.com/BonsaiDen/Atarashii/issues#issue/6

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

