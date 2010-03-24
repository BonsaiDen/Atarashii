#### Disclaimer
This project is still under heavy development, addition average is about ~1300 lines per day. Bugs getting squished every minute or so... which explains the crazy version numbering.
But besides that it's already pretty stable, most times it's best to fetch from the repo instead of using the pre build DEBIAN-Package in the downloads section.

# Atarashii
**Atarashii** is a simple Twitter Client for your GNOME Desktop.

It uses *GTK+* and *Webkit* to archive a slim and functional design.  
The code itself is written in *Python* and uses the corresponding *Python* bindings for the *GTK+* libraries.

*And **Kittens** like it!*

## Installation
There are currently three ways for you to get **Atarashii**.
  

**#1: Use the pre build Package - The way of the user...**  
This is most likely the simpelst one is to install the pre build Debian-Package from the Downloads section:  
[Click here to download the lastest version](http://github.com/downloads/BonsaiDen/Atarashii/atarashii_0.99.16-1_all.deb).

> The package will automatically setup the repo config and install the public key,  
> so you don't have to check for updates on GitHub, instead just use your systems update manager.


**#2: Install from the repo - GIT lovers choice**  
Open a shell and issue the following commands  
`git clone git://github.com/BonsaiDen/Atarashii.git`  
`./make`  
After that just run the created Debian-Package.

> You may need to install `fakeroot` via the package manager in order to be able to build the package.
> Also there is a rare bug where dpkg-deb fails to open/find the control file. If you encounter this please send me a mail with more details.


**#3: Debug without installing - For real Coding Kittens!**  
If you want to hack on **Atarashii** you can just clone the repo and then run `./debug` to start Atarashii.
> Due to hardlinks in the CSS file the favorite/reply icons won't work until **Atarashii** has been installed with one of the above methods.


## TODO
- Add more translations(See <http://github.com/BonsaiDen/Atarashii/issues#issue/6>)
- Implement a search view

## Contributing
The source is available on GitHub (<http://github.com/BonsaiDen/Atarashii>), to
contribute to the project, fork it on GitHub and send a pull request.
Everyone is welcome to make improvements to **Atarashii**!

## License
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

