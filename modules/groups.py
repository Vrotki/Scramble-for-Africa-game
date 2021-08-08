import time
from .mobs import mob
from .tiles import tile
from .tiles import veteran_icon
from .buttons import button
from . import actor_utility
from . import text_tools
from . import dice_utility
from . import utility
from . import notification_tools
from . import dice
from . import scaling
from . import main_loop_tools

class group(mob):
    '''
    Mob that is created by a combination of a worker and officer, can have unique capabilities, and restores its worker and officer upon being disbanded
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel coordinates of the bottom left of the notification
            grids: list of grid objects on which the mob's images will appear
            image_id: string representing the file path to the mob's default image
            name: string representing the mob's name
            modes: list of strings representing the game modes in which the mob can appear
            worker: worker object representing the worker that is part of this group
            officer: officer object representing the officer that is part of this group
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.worker = worker
        self.officer = officer
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.worker.join_group()
        self.officer.join_group()
        
        for current_commodity in self.global_manager.get('commodity_types'): #merges individual inventory to group inventory and clears individual inventory
            self.change_inventory(current_commodity, self.worker.get_inventory(current_commodity))
            self.change_inventory(current_commodity, self.officer.get_inventory(current_commodity))
        self.worker.inventory_setup()
        self.officer.inventory_setup()
        self.select()
        self.veteran = self.officer.veteran
        if self.veteran:
            self.set_name('Veteran expedition')
        self.veteran_icons = self.officer.veteran_icons
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.actor = self
        self.global_manager.get('group_list').append(self)
        if self.worker.movement_points > self.officer.movement_points: #a group should keep the lowest movement points out of its members
            self.set_movement_points(self.officer.movement_points)
        else:
            self.set_movement_points(self.worker.movement_points)

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Input:
            grid object representing the grid to which the group is transferring, tuple of two int variables representing the coordinates to which the group will move on the new grid
        Output:
            Moves this group and all of its images to the inputted grid at the inputted coordinates. A group will also move its attached officer, worker, and veteran icons to the new grid.
        '''
        if self.veteran:
            for current_veteran_icon in self.veteran_icons:
                current_veteran_icon.remove()
            self.veteran_icons = []
        super().go_to_grid(new_grid, new_coordinates)
        if self.veteran:
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self, self.global_manager))
        self.officer.go_to_grid(new_grid, new_coordinates)
        self.officer.join_group() #hides images
        self.worker.go_to_grid(new_grid, new_coordinates)
        self.worker.join_group()

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this group's tooltip to what it should be. A group's tooltip shows the name of the group, its officer, its worker, and its movement points.
        '''
        self.set_tooltip(["Name: " + self.name, '    Officer: ' + self.officer.name, '    Worker: ' + self.worker.name, "Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points)])

    def disband(self):
        '''
        Input:
            none
        Output:
            Separates this group into its components, giving its inventory to the officer and setting their number of movement points to that of the group
        '''
        self.officer.inventory = self.inventory
        self.inventory_setup() #reset inventory to empty
        self.remove()
        self.worker.leave_group(self)
        self.worker.set_movement_points(self.movement_points)
        self.officer.veteran_icons = self.veteran_icons
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.actor = self.officer
        self.officer.veteran = self.veteran
        self.officer.leave_group(self)
        self.officer.set_movement_points(self.movement_points)

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the group from relevant lists and prevents it from further appearing in or affecting the program.
            However, a group will not automatically remove its officer and worker when removed, since disbanding a group removes the group but not its members - to remove the members, use the die function instead
        '''
        super().remove()
        self.global_manager.set('group_list', utility.remove_from_list(self.global_manager.get('group_list'), self))

    def die(self):
        '''
        Input:
            none
        Output:
            Removes the group and its members from relevant lists and prevents them from further appearing in or affecting the program.
        '''
        self.remove()
        self.officer.remove()
        self.worker.remove()

    def update_veteran_icons(self):
        '''
        Input:
            none
        Output:
            Moves this group's veteran icons to follow its images
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

class expedition(group):
    '''
    A group with an explorer officer that is able to explore
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Input:
            same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.exploration_mark_list = []
        self.exploration_cost = 2
        self.can_explore = True

    '''def can_move(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        result = super().can_move(x_change, y_change)
        if result == False and 
        if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
            if not self.grid.find_cell(future_x, future_y).terrain == 'water':
                return(True)
            else:
                :
                    text_tools.print_to_screen("You can't move into the water.", self.global_manager) #to do: change this when boats are added
                    return(False)
                if not self.grid.find_cell(future_x, future_y).visible:
                    return(True) #will attempt to move there and discover it and discover it
        else:
            text_tools.print_to_screen("You can't move off of the map.", self.global_manager)
            return(False)'''

    def display_exploration_die(self, coordinates, result):
        '''
        Input:
            tuple of two int variables representing the pixel coordinates at which to display the die, int representing the final result that the die will roll
        Output:
            Creates a die object at the inputted coordinates that will roll, eventually stopping displaying the inputted result with an outline depending on the outcome.
            If multiple dice are present, only the die with the highest result will be outlined, showing that it was chosen.
        '''
        result_outcome_dict = {'min_success': 4, 'min_crit_success': 6, 'max_crit_fail': 1}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic'], 6, result_outcome_dict, outcome_color_dict, result, self.global_manager)

    def move(self, x_change, y_change):
        '''
        Input:
            Same as superclass
        Output:
            Same as superclass when moving into explored areas.
            When moving into explored areas, the expedition will attempt to explore there, showing a series of notifications and dice rolls.
            An exploration will result in the death of the expedition, no change, exploring the area, or exploring the area and promoting to the expedition's officer to a veteran, depending on the dice roll's result.
            Within the move function, an exploration's result will be determined. However, its outcome will not be shown until the last of the exploration notifications is shown, at which point the outcome is
            shown through the complete_exploration function.
        '''
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('show_minimap_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected
        self.global_manager.set('last_minimap_outline_switch', time.time())
        future_x = self.x + x_change
        future_y = self.y + y_change
        roll_result = 0
        if x_change > 0:
            direction = 'east'
        elif x_change < 0:
            direction = 'west'
        elif y_change > 0:
            direction = 'north'
        elif y_change < 0:
            direction = 'south'
        else:
            direction = 'none'
        future_cell = self.grid.find_cell(future_x, future_y)
        if future_cell.visible == False: #if moving to unexplored area, try to explore it
            choice_info_dict = {'expedition': self, 'x_change': x_change, 'y_change': y_change, 'cost': self.exploration_cost}
            notification_tools.display_choice_notification('Are you sure you want to attempt an exploration? It would cost ' + str(choice_info_dict['cost']) + ' money to attempt an exploration.',
                                                            ['exploration', 'none'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
            
        else: #if moving to explored area, move normally
            super().move(x_change, y_change)

    def start_exploration(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        roll_result = 0
        if x_change > 0:
            direction = 'east'
        elif x_change < 0:
            direction = 'west'
        elif y_change > 0:
            direction = 'north'
        elif y_change < 0:
            direction = 'south'
        else:
            direction = 'none'
        future_cell = self.grid.find_cell(future_x, future_y)
        self.just_promoted = False
        self.global_manager.set('ongoing_exploration', True)
        for current_grid in self.grids:
            coordinates = (0, 0)
            if current_grid.is_mini_grid:
                coordinates = current_grid.get_mini_grid_coordinates(self.x + x_change, self.y + y_change)
            else:
                coordinates = (self.x + x_change, self.y + y_change)
            self.exploration_mark_list.append(tile(coordinates, current_grid, 'misc/exploration_x/' + direction + '_x.png', 'exploration mark', ['strategic'], False, self.global_manager))
        text = ""
        text += "The expedition heads towards the " + direction + ". /n"
        text += (self.global_manager.get('flavor_text_manager').generate_flavor_text('explorer') + " /n")
            
        notification_tools.display_notification(text + "Click to roll.", 'exploration', self.global_manager)
            
        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)
            
        text += "/n"

        if self.veteran:
            text += ("The veteran explorer can roll twice and pick the higher result /n")
                
            first_roll_list = dice_utility.roll_to_list(6, "Exploration roll", 4, 6, 1, self.global_manager)
            self.display_exploration_die((500, 500), first_roll_list[0])
                                
            second_roll_list = dice_utility.roll_to_list(6, "Exploration roll", 4, 6, 1, self.global_manager)
            self.display_exploration_die((500, 380), second_roll_list[0])
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {1: "CRITICAL FAILURE", 2: "FAILURE", 3: "FAILURE", 4: "SUCCESS", 5: "SUCCESS", 6: "CRITICAL SUCCESS"}
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Exploration roll", 4, 6, 1, self.global_manager)
            self.display_exploration_die((500, 440), roll_list[0])
                
            text += roll_list[1]
            roll_result = roll_list[0]
                    
        notification_tools.display_notification(text + "Click to continue.", 'exploration', self.global_manager)
            
        text += "/n"
        if roll_result >= 4: #4+ required on D6 for exploration
            if not future_cell.resource == 'none':
                text += "You discovered a " + future_cell.terrain.upper() + " tile with a " + future_cell.resource.upper() + " resource. /n"
            else:
                text += "You discovered a " + future_cell.terrain.upper() + " tile. /n"
        else:
            text += "You were not able to explore the tile. /n"
        if roll_result == 1:
            text += "Everyone in the expedition has died. /n" #actual death occurs when exploration completes

        if (not self.veteran) and roll_result == 6:
            self.veteran = True
            self.just_promoted = True
            text += "This explorer has become a veteran explorer. /n"
        if roll_result >= 4:
            self.destination_cell = future_cell
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_exploration', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('exploration_result', [self, roll_result, x_change, y_change])

    def complete_exploration(self): #roll_result, x_change, y_change
        '''
        Input:
            none
        Output:
            Shows the outcome of an exploration attempt, which was previously determined in the move function
        '''
        exploration_result = self.global_manager.get('exploration_result')
        roll_result = exploration_result[1]
        x_change = exploration_result[2]
        y_change = exploration_result[3]
        future_cell = self.grid.find_cell(x_change + self.x, y_change + self.y)
        died = False
        if roll_result >= 4:
            future_cell.set_visibility(True)
            if not future_cell.terrain == 'water':
                super().move(x_change, y_change)
            else: #if discovered a water tile, update minimap but don't move there
                self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
                self.change_movement_points(-1 * self.movement_cost) #when exploring, movement points should be consumed regardless of exploration success or destination
        else:
            self.change_movement_points(-1 * self.movement_cost) #when exploring, movement points should be consumed regardless of exploration success or destination
        if self.just_promoted:
            self.set_name("Veteran expedition")
            self.officer.set_name("Veteran explorer")
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self, self.global_manager))
        elif roll_result == 1:
            self.die()
            died = True
        copy_dice_list = self.global_manager.get('dice_list')
        for current_die in copy_dice_list:
            current_die.remove()
        copy_exploration_mark_list = self.exploration_mark_list
        for current_exploration_mark in copy_exploration_mark_list:
            current_exploration_mark.remove()
        self.exploration_mark_list = []
        self.global_manager.set('ongoing_exploration', False)

class merge_button(button):
    '''
    Button that, when pressed, merges a selected officer with a worker in the same tile
    '''
    def __init__(self, coordinates, width, height, color, keybind_id, modes, image_id, global_manager):
        '''
        Input:
            same as superclass, except button_type is set to 'merge'
        '''
        super().__init__(coordinates, width, height, color, 'merge', keybind_id, modes, image_id, global_manager)
        
    def can_show(self):
        '''
        Input:
            none
        Output:
            Returns whether the merge button should be shown. A merge button is shown when only an officer is selected and the officer is in the same tile as a worker.
        '''
        if actor_utility.can_merge(self.global_manager):
            return(True)
        else:
            return(False)

    def on_click(self):
        '''
        Input:
            none
        Output:
            Controls the button's behavior when clicked. The merge button will cause the selected officer to form a group with a worker in the same tile.
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if len(selected_list) == 1:
                    officer = 'none'
                    worker = 'none'
                    for current_selected in selected_list:
                        if current_selected in self.global_manager.get('officer_list'):
                            officer = current_selected
                            worker = officer.images[0].current_cell.get_worker()
                    if not (officer == 'none' or worker == 'none'): #if worker and officer selected
                        if officer.x == worker.x and officer.y == worker.y:
                            create_group(officer.images[0].current_cell.get_worker(), officer, self.global_manager)
                        else:
                            text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not form a group.", self.global_manager)

class split_button(button):
    '''
    Button that, when pressed, splits a selected group into its officer and worker
    '''
    def __init__(self, coordinates, width, height, color, keybind_id, modes, image_id, global_manager):
        super().__init__(coordinates, width, height, color, 'split', keybind_id, modes, image_id, global_manager)
        
    def can_show(self):
        if actor_utility.can_split(self.global_manager):
            return(True)
        else:
            return(False)

    def on_click(self):
        '''
        Input:
            none
        Output:
            Controls the button's behavior when clicked. The merge button requires that only a group is selected, and will cause the selected group to split into its officer and worker, destroying the group.
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if len(selected_list) == 1 and selected_list[0] in self.global_manager.get('group_list'):
                    selected_list[0].disband()
                else:
                    text_tools.print_to_screen("You must have a group selected to split it into a worker and and officer.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not split a group.", self.global_manager)

def create_group(worker, officer, global_manager):
    '''
    Input:
        worker object representing the worker that will join the group, officer object representing the officer that will join the group, global_manager_template object
    Output:
        Causes the inputted officer to form a group with inputted worker.
        The type of group formed will depend on the type of officer. An explorer officer will create an expedition, which is able to explore.
        The formed group's inventory will be the combination of the inventories of the officer and the worker.
        Upon joining a group, the worker and officer will be stored by the group and will not be able to be seen or selected.
        Upon the disbanding of a group, its worker and officer will be restored and placed in the same tile as the group, with the officer being given the group's inventory.
    '''
    if officer.officer_type == 'explorer':
        new_group = expedition((officer.x, officer.y), officer.grids, 'mobs/explorer/expedition.png', 'Expedition', officer.modes, worker, officer, global_manager)
    else:
        new_group = group((officer.x, officer.y), officer.grids, 'mobs/default/default.png', 'Expedition', officer.modes, worker, officer, global_manager)