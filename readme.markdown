#### Disclaimer
This project is still under heavy development, addition average is about ~1300 lines per day. Bugs getting squished every minute or so... which explains the crazy version numbering.
But besides that it's already pretty stable, most times it's best to fetch from the repo instead of using the pre build DEBIAN-Package in the downloads section.

# Atarashii
**Atarashii** is a simple Twitter Client for your GNOME Desktop.

It uses *GTK+* and *Webkit* to archive a slim and functional design.  
The code itself is written in *Python* and uses the corresponding *Python* bindings for the *GTK+* libraries.

*And **Kittens** like it!*

## Installation
To install **Atarashii** from source run `python make.py` to create the debian package, after that just install the package that was created. 

Alternatively, you can check for a recent DEBIAN-Package at the downloads section on GitHub (<http://github.com/BonsaiDen/Atarashii/downloads>).
Atarashii has been successfully installed on two distinct Ubuntu 9.10 systems, if you encounter any problems please send me an e-mail at <ivo.wetzel@googlemail.com> or file an issues at GitHub.

#### Notes
> If you've downloaded the source you can start **Atarashii** without installing it by running `python debug.py`.
> You may need to install `fakeroot` via the package manager in order to be able to create the package by yourself.

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

