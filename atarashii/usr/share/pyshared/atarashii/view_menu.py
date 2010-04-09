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


# HTML View / Popup Menu / Tooltips --------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import send

from language import LANG as lang
from utils import URLExpander, escape, menu_escape


# This is the hacked part of Atarashii, getting this menu to work is quite a
# pain. The kittens spend some real time developing this...
class ViewMenu(object):
    def on_link_hover(self, view, title, url):
        # url might be none!
        self.last_hovered_link = url
    
    def expand_link(self, url, expanded):
        self.expanded_links[url] = expanded
        self.is_expanding = False
        self.fake_move(self.mouse_position)
    
    def on_tooltip(self, icon, pos_x, pos_y, key, tip, *args):
        link = self.last_hovered_link
        if link is not None:
            if link.startswith('avatar:'):
                uri = link[7:]
                num = int(uri[:uri.find(':')])
                user = self.get_user(num)
                img = self.get_image(num)
                
                # Set only if something has changed
                if user != self.tooltip_user \
                   or img != self.tooltip_img_file:
                    self.set_tooltip(user, img)
                    self.tooltip_user = user
                
                tip.set_custom(self.tooltip)
                return True
            
            # Try to expand links
            elif link.startswith('http://'):
                if link in self.expanded_links:
                    if self.expanded_links[link] != link:
                        tip.set_markup(lang.html_expanded_tooltip
                                       % (escape(link),
                                          escape(self.expanded_links[link])))
                        
                        return True
                
                elif not self.is_expanding:
                    self.is_expanding = True
                    URLExpander(link, self.expand_link)
    
    def set_tooltip(self, user, img):
        self.tooltip_label.set_markup(lang.html_avatar_tooltip \
                                      % (user.name, user.statuses_count,
                                      user.followers_count, user.friends_count))
        
        if img != self.tooltip_img_file:
            buf = gtk.gdk.pixbuf_new_from_file_at_size(img, 48, 48)
            self.tooltip_img.set_from_pixbuf(buf)
            self.tooltip_img_file = img
    
    
    # Menu Events --------------------------------------------------------------
    
    # Remove the default menu, this might appear besides the 'more' link
    def on_popup(self, view, menu, *args):
        menu.hide()
        menu.cancel()
        menu.destroy()
        return True
    
    def on_button(self, view, event, *args):
        self.give_text_focus = self.text.has_focus
        if event.button == 3 and not self.popup_open:
            self.menu_no_fake_move = True
            
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
            menu.connect('hide', self.on_popup_close)
            
            # This makes the menu popup just besides the mouse pointer
            # It fixes an issues were the user would release the mouse button
            # and trigger an menu item without wanting to do so
            root_pos = (int(event.x_root), int(event.y_root), True)
            menu.attach_to_widget(self, lambda *args: False)
            gobject.idle_add(menu.popup, None, None, lambda *arg: root_pos,
                             event.button, event.get_time())
            
            self.popup_open = True
            return True
    
    def add_menu_link(self, menu, name, callback, *args):
        item = gtk.MenuItem(name)
        if callback is not None:
            item.connect('activate', callback, *args)
        
        menu.append(item)
        return item
    
    def add_menu_separator(self, menu):
        item = gtk.SeparatorMenuItem()
        menu.append(item)
    
    def on_popup_close(self, *args):
        if self.friend_thread is not None:
            self.friend_thread.menu = None
            self.friend_thread = None
        
        if self.menu_no_fake_move:
            self.menu_no_fake_move = False
            self.fake_move((-1.0, -1.0))
        
        self.popup_open = False
        self.text.html_focus()
    
    
    # Menu Building ------------------------------------------------------------
    def create_base_menu(self, menu, item, link):
        link_data = self.get_link_type(link)
        link, full = link_data[0], link_data[2]
        item_id = self.get_id(item) if item is not None else -1
        if self.ok_menu(link):
            
            # Link options
            if self.create_link_menu(menu, link, full):
                return True
            
            # Status / Tag
            elif self.create_status_tag_menu(menu, link, full):
                return True
            
            else:
                # Profile
                if link in ('user', 'profile', 'rprofile', 'avatar'):
                    user = full[full.rfind('/') + 1:]
                    self.add_menu_link(menu,
                                       lang.context_profile % menu_escape(user),
                                       self.context_link, full)
                
                else:
                    user = None
                
                self.create_menu(menu, item, item_id, link, full, user)
                
                # Follow / Block
                if link in ('profile', 'avatar') \
                   and user.lower() != self.main.username.lower() \
                   and not user.lower() in self.main.follow_pending \
                   and not user.lower() in self.main.block_pending:
                    
                    self.add_menu_separator(menu)
                    self.add_menu_link(menu, lang.context_friend_loading,
                                       None).set_sensitive(False)
                    
                    self.friend_thread = send.Friends(self.main, user, menu,
                                                      self.create_friend_menu)
                
                return True
        
        else:
            return False
    
    def create_friend_menu(self, menu, friend):
        items = menu.get_children()
        if friend is not None:
            menu.remove(items[-1])
            name = friend[1].screen_name
            info = lang.context_friend_unfollow % menu_escape(name) \
                   if friend[0].following \
                   else lang.context_friend_follow % menu_escape(name)
            
            self.add_menu_link(menu, info, self.main.follow,
                               friend[1].id, name, not friend[0].following)
            
            info = lang.context_friend_unblock % menu_escape(name) \
                   if friend[0].blocking \
                   else lang.context_friend_block % menu_escape(name)
            
            self.add_menu_link(menu, info, self.main.block,
                               friend[1].id, name, not friend[0].blocking)
            
            menu.show_all()
        
        else:
            menu.remove(items[-2])
            menu.remove(items[-1])
    
    def create_link_menu(self, menu, link, full):
        if link == 'link':
            self.add_menu_link(menu, lang.context_browser,
                               self.context_link, full)
            
            self.add_menu_link(menu, lang.context_copy,
                               self.copy_link, full)
            return True
    
    def create_status_tag_menu(self, menu, link, full):
        if link == 'status':
            self.add_menu_link(menu, lang.context_view,
                               self.context_link, full)
            return True
        
        elif link == 'tag':
            self.add_menu_link(menu, lang.context_search,
                               self.context_link, full)
            return True
    
    
    # Get a Tweet based on a button press --------------------------------------
    def get_clicked_item(self, items, event):
        if items is None:
            return -1
        
        # Get Positions and Link
        items, link = items.split('|')
        if link == 'undefined':
            link = None
        
        items = items.split(';')
        mouse_y = event.y + self.scroll.get_vscrollbar().get_value()
        item_num = -1
        last_pos = 0
        for i in items:
            data = i.split(',')
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
            var items = document.getElementsByClassName('viewitem');
            var pos = 0;
            for (var i = 0; i < items.length; i++) {
                var item = items[i];
                pos += item.offsetHeight;
                sizes.push([item.getAttribute('id'), pos])
                pos += 2;
                delete item;
            };
            delete pos;
            delete items;
            var link = document.elementFromPoint(%d, %d);
            document.title = sizes.join(';') + '|' +
            (link.href != undefined ? link.href : link.parentNode.href);
            delete link;
            delete sizes;''' % (event.x, event.y))
            title = self.get_main_frame().get_title()
            return title
        
        except Exception:
            return None

