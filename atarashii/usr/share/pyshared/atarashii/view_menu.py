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


# HTML View / Popup Menu -------------------------------------------------------
# ------------------------------------------------------------------------------
import gobject
import gtk

from language import LANG as lang


# This is the hacked part of Atarashii, getting this menu to work is quite a 
# pain. The kittens spend some real time developing this...
class ViewMenu:
    def __init__(self):
        pass
    
    # Event
    def on_popup(self, view, menu, *args): # Kill of the original context menu!
        menu.hide()
        menu.cancel()
        menu.destroy()
        return True
    
    # Let's create our own nice little popup :)
    def on_button(self, view, event, *args):
        # Give back focus to textbox
        if self.give_text_focus:
            gobject.idle_add(self.gui.text.grab_focus)
            self.give_text_focus = False
        
        if event.button == 3:
            # Calculate on which item the user clicked
            item_id, link = self.get_clicked_item(self.get_sizes(event), event)
            if item_id == -1:
                return False
            
            item = self.items[item_id][0]
            
            # Create Menu
            menu = gtk.Menu()
            if not self.create_base_menu(menu, item, link):
                return False
            
            if len(menu.get_children()) == 0:
                return False
            
            menu.show_all()
            menu.connect("hide", self.on_popup_close)
            
            # This makes the menu popup just besides the mouse pointer
            # It fixes an issues were the user would release the mouse button
            # and trigger an menu item without wanting to do so
            def position(*args):
                return (int(event.x_root), int(event.y_root), True)
            
            menu.attach_to_widget(self, lambda *args: False)
            menu.popup(None, None, position, event.button, event.get_time())
            return True
    
    def add_menu_link(self, menu, name, callback):
        item = gtk.MenuItem()
        item.set_label(name)
        item.connect('activate', callback)
        menu.append(item)
    
    def add_menu_separator(self, menu):
        item = gtk.SeparatorMenuItem()
        menu.append(item)
    
    def on_popup_close(self, *args):
        self.gui.text.html_focus()
    
    
    # Menu Building ------------------------------------------------------------
    def create_base_menu(self, menu, item, link):
        link_data = self.get_link_type(link)
        link, full = link_data[0], link_data[2]
        item_id = self.get_id(item) if item != None else -1
        if self.ok_menu(link):
            if self.create_link_menu(menu, link, full): # Link options
                return True
            
            elif self.create_status_tag_menu(menu, link, full): # Status / Tag
                return True
            
            else:
                # Profile
                if link in ('user', 'profile'):
                    user = full[full.rfind("/") + 1:]
                    self.add_menu_link(menu, lang.context_profile % user,
                                       lambda *args: self.context_link(full))
                
                else:
                    user = None
                
                return self.create_menu(menu, item, item_id, link, full, user)
        
        else:
            return False
    
    def create_link_menu(self, menu, link, full):
        if link == "link":
            self.add_menu_link(menu, lang.context_browser,
                               lambda *args: self.context_link(full))
            
            self.add_menu_link(menu, lang.context_copy,
                               lambda *args: self.copy_link(full))  
            return True
    
    def create_status_tag_menu(self, menu, link, full):
        if link == "status":
            self.add_menu_link(menu, lang.context_view,
                               lambda *args: self.context_link(full))
            return True
        
        elif link == "tag":
            self.add_menu_link(menu, lang.context_search,
                               lambda *args: self.context_link(full))   
            return True
    
    
    # Get a Tweet based on a button press --------------------------------------
    def get_clicked_item(self, items, event):
        if items == None:
            return -1
        
        # Get Positions and Link
        items, link = items.split("|")
        if link == "undefined":
            link = None
        
        items = items.split(";")
        mouse_y = event.y + self.scroll.get_vscrollbar().get_value()
        item_num = -1
        last_pos = 0
        for i in items:
            data = i.split(",")
            if len(data) > 1:
                pos = int(data[1])
                if mouse_y >= last_pos and mouse_y < pos:
                    item_num = int(data[0])
                    break
                
                last_pos = pos
        
        return item_num, link
    
    # Run some crazy javascript in order to calculate all the positioning
    def get_sizes(self, event):
        try:
            self.execute_script('''
            var sizes = [];
            var items = document.getElementsByClassName("viewitem");
            var pos = 0;
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                pos += item.offsetHeight;
                sizes.push([item.getAttribute("id"), pos])
                pos += 2;
                delete item;
            };
            delete pos;
            delete items;
            var link = document.elementFromPoint(%d, %d);
            document.title = sizes.join(";") + "|" + 
            (link.href != undefined ? link.href : link.parentNode.href);
            delete link;
            delete sizes;''' % (event.x, event.y))
            title = self.get_main_frame().get_title()
            return title
            
        except:
            return None

