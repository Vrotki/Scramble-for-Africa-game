import pygame
import time
from . import images
from . import text_tools
from . import utility
from . import actor_utility
from .actors import actor
from .tiles import veteran_icon

class mob(actor):
    '''
    Actor that can be controlled and selected and can appear on multiple grids at once
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel coordinates of the bottom left of the notification
            grids: list of grid objects on which the mob's images will appear
            image_id: string representing the file path to the mob's default image
            name: string representing the mob's name
            modes: list of strings representing the game modes in which the mob can appear
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.selected = False
        super().__init__(coordinates, grids, modes, global_manager)
        self.image_dict = {'default': image_id}
        self.selection_outline_color = 'bright green'
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))#self, actor, width, height, grid, image_description, global_manager
        global_manager.get('mob_list').append(self)
        self.set_name(name)
        self.can_explore = False
        self.max_movement_points = 1
        self.movement_cost = 1
        self.reset_movement_points()
        self.update_tooltip()
        self.select()

    def change_movement_points(self, change):
        self.movement_points += change
        if self.global_manager.get('displayed_mob') == self: #update mob info display to show new movement points
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_movement_points(self, new_value):
        self.movement_points = new_value
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def reset_movement_points(self):
        self.movement_points = self.max_movement_points
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def change_inventory(self, commodity, change):
        '''
        Input:
            same as superclass
        Output:
            same as superclass, except, if currently being shown in the mob info display, updates the displayed commodities to reflect the change
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Input:
            same as superclass
        Output:
            same as superclass, except, if currently being shown in the mob info display, updates the displayed commodities to reflect the change
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Input:
            grid object representing the grid to which the mob is transferring, tuple of two int variables representing the coordinates to which the mob will move on the new grid
        Output:
            Moves this mob and all of its images to the inputted grid at the inputted coordinates
        '''
        if new_grid == self.global_manager.get('europe_grid'):
            self.modes.append('europe')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), 'none')
        else:
            self.modes = utility.remove_from_list(self.modes, 'europe')
        self.x, self.y = new_coordinates
        for current_image in self.images:
            current_image.remove_from_cell()
            self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), current_image))
        self.grids = [new_grid]
        self.grid = new_grid
        if not new_grid.mini_grid == 'none':
            new_grid.mini_grid.calibrate(new_coordinates[0], new_coordinates[1])
            self.grids.append(new_grid.mini_grid)
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))
            self.images[-1].add_to_cell()

    def select(self):
        '''
        Input:
            none
        Output:
            Causes this mob to be selected and causes the selection outline timer to be reset, displaying it immediately
        '''
        self.selected = True
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected
        if self.images[0].current_cell.contained_mobs[0] == self: #only calibrate actor info if top of stack
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def draw_outline(self):
        '''
        Input:
            none
        Output:
            If selection outlines are currently allowed to appear and if this mob is showing, draw a selection outline around each of its images
        '''
        if self.global_manager.get('show_selection_outlines'):
            for current_image in self.images:
                if not current_image.current_cell == 'none' and self == current_image.current_cell.contained_mobs[0]: #only draw outline if on top of stack
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (current_image.outline), current_image.outline_width)
        
    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this mob's tooltip to its name and movement points
        '''
        self.set_tooltip(["Name: " + self.name, "Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points)])

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        if (not self.images[0].current_cell == 'none') and (not self.images[0].current_cell.tile == 'none'): #drop inventory on death
            current_tile = self.images[0].current_cell.tile
            for current_commodity in self.global_manager.get('commodity_types'):
                current_tile.change_inventory(current_commodity, self.get_inventory(current_commodity))
        if self.selected:
            self.selected = False
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), 'none')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), 'none')
        for current_image in self.images:
            current_image.remove_from_cell()
        super().remove()
        self.global_manager.set('mob_list', utility.remove_from_list(self.global_manager.get('mob_list'), self)) #make a version of mob_list without self and set mob_list to it

    def can_move(self, x_change, y_change):
        '''
        Input:
            int representing the distance moved to the right from a proposed movement, int representing the distance moved upward from a proposed movement
        Output:
            Returns whether the proposed movement would be possible
        '''
        future_x = self.x + x_change
        future_y = self.y + y_change
        if not self.grid in self.global_manager.get('abstract_grid_list'):
            if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
                if self.grid.find_cell(future_x, future_y).visible or self.can_explore:
                    if not self.grid.find_cell(future_x, future_y).terrain == 'water':
                        if self.movement_points >= self.movement_cost:
                            return(True)
                        else:
                            text_tools.print_to_screen("You do not have enough movement points to move.", self.global_manager)
                            text_tools.print_to_screen("You have " + str(self.movement_points) + " movement points while " + str(self.movement_cost) + " are required.", self.global_manager)
                            return(False)
                    else:
                        if self.grid.find_cell(future_x, future_y).visible or self.can_explore:
                            text_tools.print_to_screen("You can't move into the water.", self.global_manager) #to do: change this when boats are added
                            return(False)
                else:
                    text_tools.print_to_screen("You can't move into an unexplored tile.", self.global_manager)
                    return(False)
            else:
                text_tools.print_to_screen("You can't move off of the map.", self.global_manager)
                return(False)
        else:
            text_tools.print_to_screen("You can not move while in this area.", self.global_manager)
            return(False)

    def move(self, x_change, y_change):
        '''
        Input:
            int representing the distance moved to the right, int representing the distance moved upward
        Output:
            Moves this mob x_change tiles to the right and y_change tiles upward
        '''
        for current_image in self.images:
            current_image.remove_from_cell()
        self.x += x_change
        self.y += y_change
        #self.inventory['coffee'] += 1 #test showing how to add to inventory
        self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        for current_image in self.images:
            current_image.add_to_cell()
        self.change_movement_points(-1 * self.movement_cost)
        #self.change_inventory(random.choice(self.global_manager.get('commodity_types')), 1)

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether any of this mob's images are colliding with the mouse
        '''
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                    return(True)
        return(False) #return false if none touch mouse

    def set_name(self, new_name):
        '''
        Input:
            same as superclass
        Output:
            same as superclass, except, if currently being shown in the mob info display, updates the displayed name 
        '''
        super().set_name(new_name)
        if self.global_manager.get('displayed_mob') == self: #self.selected:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

class worker(mob):
    '''
    Mob that is considered a worker and can join groups
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            same as superclass 
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('worker_list').append(self)
        self.in_group = False

    def can_show_tooltip(self):
        '''
        Input:
            none
        Output:
            Same as superclass but only returns True if not part of a group
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes and not self.in_group: #and not targeting_ability
            return(True)
        else:
            return(False)

    def join_group(self):
        '''
        Input:
            none
        Output:
            Prevents this worker from being seen and interacted with, storing it as part of a group
        '''
        self.in_group = True
        self.selected = False
        for current_image in self.images:
            current_image.remove_from_cell()

    def leave_group(self, group):
        '''
        Input:
            group object from which this worker is leaving
        Output:
            Allows this worker to be seen and interacted with, moving it to where the group was disbanded
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        for current_image in self.images:
            current_image.add_to_cell()
        #self.select()

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('worker_list', utility.remove_from_list(self.global_manager.get('worker_list'), self))

class officer(mob):
    '''
    Mob that is considered an officer and can join groups and become a veteran
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            Same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('officer_list').append(self)
        self.veteran = False
        self.veteran_icons = []
        self.in_group = False
        self.officer_type = 'default'

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Input:
            Same as superclass
        Output:
            Same as superclass, except it also moves veteran icons to the new grid and coordinates
        '''
        if (not self.in_group) and self.veteran:
            for current_veteran_icon in self.veteran_icons:
                current_veteran_icon.remove()
            self.veteran_icons = []
        super().go_to_grid(new_grid, new_coordinates)
        if (not self.in_group) and self.veteran:
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self, self.global_manager))

    def can_show_tooltip(self):
        '''
        Input:
            none
        Output:
            Same as superclass but only returns True if not part of a group
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes and not self.in_group: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def join_group(self):
        '''
        Input:
            none
        Output:
            Prevents this officer from being seen and interacted with, storing it as part of a group
        '''
        self.in_group = True
        self.selected = False
        for current_image in self.images:
            current_image.remove_from_cell()

    def leave_group(self, group):
        '''
        Input:
            group object from which this officer is leaving
        Output:
            Allows this officer to be seen and interacted with, moving it to where the group was disbanded
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.update_veteran_icons()
        for current_image in self.images:
            current_image.add_to_cell()
        self.select()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #calibrate info display to officer's tile upon disbanding

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('officer_list', utility.remove_from_list(self.global_manager.get('officer_list'), self))
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.remove()

    def update_veteran_icons(self):
        '''
        Input:
            none
        Output:
            Moves this officer's veteran icons to follow its images
        '''
        for current_veteran_icon in self.veteran_icons:
            if current_veteran_icon.grid.is_mini_grid:
                current_veteran_icon.x, current_veteran_icon.y = current_veteran_icon.grid.get_mini_grid_coordinates(self.x, self.y)
            else:
                current_veteran_icon.x = self.x
                current_veteran_icon.y = self.y

    def move(self, x_change, y_change):
        '''
        Input:
            Same as superclass
        Output:
            Same as superclass but also moves its veteran icons to follow its images
        '''
        super().move(x_change, y_change)
        self.update_veteran_icons()

class explorer(officer):
    '''
    Officer that is considered an explorer
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            Same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.grid.find_cell(self.x, self.y).set_visibility(True)
        self.officer_type = 'explorer'