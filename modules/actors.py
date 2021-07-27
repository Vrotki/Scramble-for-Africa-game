import pygame
import time
from . import images
from . import text_tools
from . import dice_utility
from . import utility
from . import notification_tools
#from . import label
from . import dice
from . import scaling
from . import actor_utility

class actor():
    def __init__(self, coordinates, grids, modes, global_manager):
        self.global_manager = global_manager
        global_manager.get('actor_list').append(self)
        self.modes = modes
        self.grids = grids
        self.grid = grids[0]
        self.x, self.y = coordinates
        self.name = ''
        self.set_name('placeholder')
        self.set_coordinates(self.x, self.y, False)
        #self.controllable = False# obsolete but possibly usable later
        self.selected = False
    
    def set_name(self, new_name):
        self.name = new_name        
       
    def is_clear(self, x, y):
        return self.grid.is_clear(x, y)
    
    def set_coordinates(self, x, y, able_to_print):
        if self.is_clear(x, y):
            self.grid.find_cell(self.x, self.y).occupied = False
            self.x = x
            self.y = y
            self.grid.find_cell(self.x, self.y).occupied = True
        else:#elif able_to_print:
            text_tools.print_to_screen('This cell is blocked.', self.global_manager)
            
    def set_tooltip(self, new_tooltip):
        for current_image in self.images:
            current_image.set_tooltip(new_tooltip)
    
    def update_tooltip(self):
        self.set_tooltip(['Name: ' + self.name])
        
    def remove(self):
        self.global_manager.set('actor_list', utility.remove_from_list(self.global_manager.get('actor_list'), self))
        for current_image in self.images:
            self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), current_image))

    def interact(self, other):
        if other == None:
            text_tools.print_to_screen(self.name + ' has nothing to interact with.')
        else:
            text_tools.print_to_screen(self.name + ' is interacting with ' + other.name)

    def touching_mouse(self):
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                return(True)
        return(False) #return false if none touch mouse

    def can_show_tooltip(self): #moved to actor
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def draw_tooltip(self, y_displacement):
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tooltip_image = self.images[0]
        for current_image in self.images: #only draw tooltip from the image that the mouse is touching
            if current_image.Rect.collidepoint((mouse_x, mouse_y)):
                tooltip_image = current_image
        mouse_y += y_displacement
        if (mouse_x + tooltip_image.tooltip_box.width) > self.global_manager.get('display_width'):
            mouse_x = self.global_manager.get('display_width') - tooltip_image.tooltip_box.width
        if (self.global_manager.get('display_height') - mouse_y) - (len(tooltip_image.tooltip_text) * self.global_manager.get('font_size') + 5 + tooltip_image.tooltip_outline_width) < 0:
            mouse_y = self.global_manager.get('display_height') - tooltip_image.tooltip_box.height
        tooltip_image.tooltip_box.x = mouse_x
        tooltip_image.tooltip_box.y = mouse_y
        tooltip_image.tooltip_outline.x = tooltip_image.tooltip_box.x - tooltip_image.tooltip_outline_width
        tooltip_image.tooltip_outline.y = tooltip_image.tooltip_box.y - tooltip_image.tooltip_outline_width
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], tooltip_image.tooltip_outline)
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], tooltip_image.tooltip_box)
        for text_line_index in range(len(tooltip_image.tooltip_text)):
            text_line = tooltip_image.tooltip_text[text_line_index]
            self.global_manager.get('game_display').blit(text_tools.text(text_line, self.global_manager.get('myfont'), self.global_manager), (tooltip_image.tooltip_box.x + 10, tooltip_image.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))
            
class mob(actor):
    '''a mobile and selectable actor'''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, modes, global_manager)
        self.image_dict = {'default': image_id}
        #self.grids = grids #for things like drawing images on each grid, go through each grid on which the mob can appear # moved to actor class
        #self.grid = grids[0] #for things like detecting if moving is possible, use the first grid, which will be the main map
        self.selection_outline_color = 'bright green'
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))#self, actor, width, height, grid, image_description, global_manager
            
        global_manager.get('mob_list').append(self)
        self.set_name(name)
        self.update_tooltip()

    def select(self):
        self.selected = True
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected

    def draw_outline(self):
        if self.global_manager.get('show_selection_outlines'):
            for current_image in self.images:
                if not current_image.current_cell == 'none' and self == current_image.current_cell.contained_mobs[0]: #only draw outline if on top of stack
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (current_image.outline), current_image.outline_width)
        
    def update_tooltip(self):
        self.set_tooltip([self.name])

    def remove(self):
        for current_image in self.images:
            current_image.remove_from_cell()
        super().remove()
        self.global_manager.set('mob_list', utility.remove_from_list(self.global_manager.get('mob_list'), self)) #make a version of mob_list without self and set mob_list to it

    def can_move(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
            if self.grid.find_cell(future_x, future_y).visible:
                if not self.grid.find_cell(future_x, future_y).terrain == 'water':
                    return(True)
                else:
                    if self.grid.find_cell(future_x, future_y).visible:
                        text_tools.print_to_screen("You can't move into the water.", self.global_manager) #to do: change this when boats are added
                        return(False)
            else:
                text_tools.print_to_screen("You can't move into an unexplored tile.", self.global_manager)
                return(False)

        else:
            text_tools.print_to_screen("You can't move off of the map.", self.global_manager)
            return(False)

    def move(self, x_change, y_change):
        for current_image in self.images:
            current_image.remove_from_cell()
        self.x += x_change
        self.y += y_change
        self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        for current_image in self.images:
            #print('from here mob move')
            current_image.add_to_cell()

    def touching_mouse(self):
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                    return(True)
        return(False) #return false if none touch mouse

class worker(mob):
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('worker_list').append(self)
        self.in_group = False

    def can_show_tooltip(self):
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes and not self.in_group: #and not targeting_ability
            #print('true')
            return(True)
        else:
            #print('false')
            #print('touching mouse: ' + str(self.touching_mouse()))
            #print('in group: ' + str(self.in_group))
            #for current_image in self.images:
            #    if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
            #        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], current_image.Rect)
            return(False)

    def join_group(self):
        self.in_group = True
        self.selected = False
        for current_image in self.images:
            current_image.remove_from_cell()

    def leave_group(self, group):
        self.in_group = False
        self.x = group.x
        self.y = group.y
        for current_image in self.images:
            current_image.add_to_cell()
        self.select()

    def remove(self):
        super().remove()
        self.global_manager.set('worker_list', utility.remove_from_list(self.global_manager.get('worker_list'), self))

class officer(mob):
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('officer_list').append(self)
        self.veteran = False
        self.veteran_icons = []
        self.in_group = False
        self.officer_type = 'default'

    def can_show_tooltip(self): #moved to actor
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes and not self.in_group: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def join_group(self):
        self.in_group = True
        self.selected = False
        for current_image in self.images:
            current_image.remove_from_cell()

    def leave_group(self, group):
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.update_veteran_icons()
        for current_image in self.images:
            current_image.add_to_cell()
        self.select()

    def remove(self):
        super().remove()
        self.global_manager.set('officer_list', utility.remove_from_list(self.global_manager.get('officer_list'), self))
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.remove()

    def update_veteran_icons(self):
        for current_veteran_icon in self.veteran_icons:
            if current_veteran_icon.grid.is_mini_grid:
                current_veteran_icon.x, current_veteran_icon.y = current_veteran_icon.grid.get_mini_grid_coordinates(self.x, self.y)
            else:
                current_veteran_icon.x = self.x
                current_veteran_icon.y = self.y

    def move(self, x_change, y_change):
        super().move(x_change, y_change)
        self.update_veteran_icons()
        #print(self.veteran_icons)

class explorer(officer):
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.grid.find_cell(self.x, self.y).set_visibility(True)
        self.officer_type = 'explorer'

class tile_class(actor): #to do: make terrain tiles a subclass
    '''like an obstacle without a tooltip or movement blocking'''
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, global_manager): #show_terrain is like a subclass, true is terrain tile, false is non-terrain tile
        super().__init__(coordinates, [grid], modes, global_manager)
        self.set_name(name)
        self.global_manager.get('tile_list').append(self)
        self.image_dict = {'default': image}
        self.image = images.tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.images = [self.image] #tiles only appear on 1 grid, have images defined to be more consistent with other actor subclasses
        #self.shader = tile_shader(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.show_terrain = show_terrain
        self.cell = self.grid.find_cell(self.x, self.y)
        #if self.cell.tile == 'none':
        #    self.cell.tile = self
        if self.show_terrain: #to do: make terrain tiles a subclass
            self.cell.tile = self
            self.resource_icon = 'none' #the resource icon is appearance, making it a property of the tile rather than the cell
            self.set_terrain(self.cell.terrain) #terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'
            self.set_visibility(self.cell.visible)
        elif self.name == 'resource icon':
            self.image_dict['hidden'] = 'misc/empty.png'
        else:
            self.terrain = 'floor'
    def set_visibility(self, new_visibility):
        if new_visibility == True:
            image_name = 'default'
        else:
            image_name = 'hidden'
            
        self.image.set_image(image_name)
        self.image.previous_idle_image = image_name
        if not self.resource_icon == 'none':
            self.resource_icon.image.set_image(image_name)
            self.resource_icon.image.previous_idle_image = image_name
            
    def set_resource(self, new_resource):
        #if self.show_terrain: #only do something if a terrain tile
            if not self.resource_icon == 'none':
                self.resource_icon.remove()
                self.resource_icon = 'none'
            self.resource = new_resource
            #if not self.cell.resource == 'none':
            self.resource_icon = tile_class((self.x, self.y), self.grid, 'scenery/resources/' + self.cell.resource + '.png', 'resource icon', ['strategic'], False, self.global_manager)
            self.set_visibility(self.cell.visible)
            
    def set_terrain(self, new_terrain): #to do, add variations like grass to all terrains
        #print(self.cell.terrain + ' ' + new_terrain)
        if new_terrain == 'clear':
            #random_grass = random.randrange(1, 3) #clear, hills, jungle, water, mountain, swamp, desert
            #self.image_dict['default'] = 'scenery/terrain/clear' + str(random_grass) + '.png'
            self.image_dict['default'] = 'scenery/terrain/clear.png'
            
        elif new_terrain == 'hills':
            self.image_dict['default'] = 'scenery/terrain/hills.png'
            
        elif new_terrain == 'jungle':
            self.image_dict['default'] = 'scenery/terrain/jungle.png'
            
        elif new_terrain == 'water':
            self.image_dict['default'] = 'scenery/terrain/water.png'
            
        elif new_terrain == 'mountain':
            self.image_dict['default'] = 'scenery/terrain/mountain.png'
            
        elif new_terrain == 'swamp':
            self.image_dict['default'] = 'scenery/terrain/swamp.png'
            
        elif new_terrain == 'desert':
            self.image_dict['default'] = 'scenery/terrain/desert.png'

        elif new_terrain == 'none':
            self.image_dict['default'] = 'scenery/hidden.png'

        self.image.set_image('default')

    def update_tooltip(self):
        if self.show_terrain: #if is terrain, show tooltip
            tooltip_message = []
            if self.cell.visible:
                tooltip_message.append('This is a ' + self.cell.terrain + ' tile.')
                if not self.cell.resource == 'none':
                    tooltip_message.append('This tile has a ' + self.cell.resource + ' resource.')
            else:
                tooltip_message .append('This tile has not been explored.')
            self.set_tooltip(tooltip_message)
        else:
            self.set_tooltip([])

    def set_coordinates(self, x, y, able_to_print):
        my_cell = self.grid.find_cell(self.x, self.y)
        #if self.is_clear(x, y):
        #my_cell.occupied = False
        self.x = x
        self.y = y
        my_cell = self.grid.find_cell(self.x, self.y)
        #my_cell.occupied = False
        #else:
        #    if self.controllable and able_to_print:
        #        text_tools.print_to_screen("You can't move to an occupied cell.")
                
    def remove(self):
        super().remove()
        self.global_manager.set('tile_list', utility.remove_from_list(self.global_manager.get('tile_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image)) #to do: see if this can be removed, should already be in actor
        #self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.shader))
        #print('removing')
        #self.cell.tile = 'none'
        #to do: this remove function is being called incorrectly at some point in the program, causing tiles to be removed

    def can_show_tooltip(self): #tiles don't have tooltips, except for terrain tiles
        if self.show_terrain == True:
            if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability
                if self.cell.terrain == 'none':
                    return(False)
                else:
                    return(True)
            else:
                return(False)
        else:
            return(False)

class veteran_icon(tile_class):
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, actor, global_manager):
        super().__init__(coordinates, grid, image, name, modes, show_terrain, global_manager)
        self.actor = actor
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        self.image = images.veteran_icon_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.images = [self.image]
        
class overlay_tile(tile_class):
    '''kind of tile, preferably transparent, that appears in front of obstacles. Good for darkness and such'''
    def __init__(self, actor, width, height, grid, image_id, show_terrain, global_manager):
        super().__init__(actor, width, height, grid, image_id, show_terrain, global_manager)
        self.global_manager.get('overlay_tile_list').append(self)
        
    def remove(self):
        super().remove()
        self.global_manager.set('overlay_tile_list', utility.remove_from_list(self.global_manager.get('overlay_tile_list'), self))

