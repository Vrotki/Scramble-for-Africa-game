#Contains functionality for player-controlled mobs

import pygame
import random
from ..mobs import mob
from ...util import text_utility, utility, actor_utility, scaling, dice_utility, turn_management_utility, minister_utility

class pmob(mob):
    '''
    Short for player-controlled mob, mob controlled by the player
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'sentry_mode': boolean value - Required if from save, whether this unit is in sentry mode, preventing it from being in the turn order
                'in_turn_queue': boolean value - Required if from save, whether this unit is in the turn order, allowing end unit turn commands, etc. to persist after saving/loading
                'base_automatic_route': int tuple list value - Required if from save, list of the coordinates in this unit's automatic movement route, with the first coordinates being the start and the last being the end. List empty if
                    no automatic movement route has been designated
                'in_progress_automatic_route': string/int tuple list value - Required if from save, list of the coordinates and string commands this unit will execute, changes as the route is executed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.sentry_mode = False
        super().__init__(from_save, input_dict, global_manager)
        self.selection_outline_color = 'bright green'
        global_manager.get('pmob_list').append(self)
        self.is_pmob = True
        self.set_controlling_minister_type('none')
        if from_save:
            if not input_dict['end_turn_destination'] == 'none': #end turn destination is a tile and can't be pickled, need to find it again after loading
                end_turn_destination_x, end_turn_destination_y = input_dict['end_turn_destination']
                end_turn_destination_grid = self.global_manager.get(input_dict['end_turn_destination_grid_type'])
                self.end_turn_destination = end_turn_destination_grid.find_cell(end_turn_destination_x, end_turn_destination_y).tile
            self.default_name = input_dict['default_name']
            self.set_name(self.default_name)
            self.set_sentry_mode(input_dict['sentry_mode'])
            self.set_automatically_replace(input_dict['automatically_replace'])
            if input_dict['in_turn_queue'] and input_dict['end_turn_destination'] == 'none':
                self.add_to_turn_queue()
            else:
                self.remove_from_turn_queue()
            self.base_automatic_route = input_dict['base_automatic_route']
            self.in_progress_automatic_route = input_dict['in_progress_automatic_route']
        else:
            self.default_name = self.name
            self.set_max_movement_points(4)
            self.set_sentry_mode(False)
            self.set_automatically_replace(True)
            self.add_to_turn_queue()
            self.base_automatic_route = [] #first item is start of route/pickup, last item is end of route/dropoff
            self.in_progress_automatic_route = [] #first item is next step, last item is current location
            actor_utility.deselect_all(self.global_manager)
            if ('select_on_creation' in input_dict) and input_dict['select_on_creation']:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), self.images[0].current_cell.tile)
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), 'none', override_exempt=True)
                self.select()
        self.attached_cell_icon_list = []

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'default_name': string value - This actor's name without modifications like veteran
                'end_turn_destination': string or int tuple value- 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'sentry_mode': boolean value - Whether this unit is in sentry mode, preventing it from being in the turn order
                'in_turn_queue': boolean value - Whether this unit is in the turn order, allowing end unit turn commands, etc. to persist after saving/loading
                'base_automatic_route': int tuple list value - List of the coordinates in this unit's automatic movement route, with the first coordinates being the start and the last being the end. List empty if
                    no automatic movement route has been designated
                'in_progress_automatic_route': string/int tuple list value - List of the coordinates and string commands this unit will execute, changes as the route is executed
                'automatically_replace': boolean value  Whether this unit or any of its components should be replaced automatically in the event of attrition
        '''
        save_dict = super().to_save_dict()
        if self.end_turn_destination == 'none':
            save_dict['end_turn_destination'] = 'none'
        else: #end turn destination is a tile and can't be pickled, need to save its location to find it again after loading
            for grid_type in self.global_manager.get('grid_types_list'):
                if self.end_turn_destination.grid == self.global_manager.get(grid_type):
                    save_dict['end_turn_destination_grid_type'] = grid_type
            save_dict['end_turn_destination'] = (self.end_turn_destination.x, self.end_turn_destination.y)
        save_dict['default_name'] = self.default_name
        save_dict['sentry_mode'] = self.sentry_mode
        save_dict['in_turn_queue'] = (self in self.global_manager.get('player_turn_queue'))
        save_dict['base_automatic_route'] = self.base_automatic_route
        save_dict['in_progress_automatic_route'] = self.in_progress_automatic_route
        save_dict['automatically_replace'] = self.automatically_replace
        return(save_dict)

    def clear_attached_cell_icons(self):
        '''
        Description:
            Removes all of this unit's cell icons
        Input:
            None
        Output:
            None
        '''
        for current_cell_icon in self.attached_cell_icon_list:
            current_cell_icon.remove_complete()
        self.attached_cell_icon_list = []

    def create_cell_icon(self, x, y, image_id):
        '''
        Description:
            Creates a cell icon managed by this mob with the inputted image at the inputted coordinates
        Input:
            int x: cell icon's x coordinate on main grid
            int y: cell icon's y coordinate on main grid
            string image_id: cell icon's image_id
            string init_type='cell icon': init type of actor to create
            dictionary extra_parameters=None: dictionary of any extra parameters to pass to the created actor
        '''
        self.attached_cell_icon_list.append(self.global_manager.get('actor_creation_manager').create(False, {
            'coordinates': (x, y),
            'grids': self.grids,
            'image': image_id,
            'modes': ['strategic'],
            'init_type': 'cell icon'
        }, self.global_manager))

    def add_to_automatic_route(self, new_coordinates):
        '''
        Description:
            Adds the inputted coordinates to this unit's automated movement route, changing the in-progress route as needed
        Input:
            int tuple new_coordinates: New x and y coordinates to add to the route
        Output:
            None
        '''
        self.base_automatic_route.append(new_coordinates)
        self.calculate_automatic_route()
        if self == self.global_manager.get('displayed_mob'):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self)

    def calculate_automatic_route(self):
        '''
        Description:
            Creates an in-progress movement route based on the base movement route when the base movement route changes
        Input:
            None
        Output:
            None
        '''
        reversed_base_automatic_route = utility.copy_list(self.base_automatic_route)
        reversed_base_automatic_route.reverse()
    
        self.in_progress_automatic_route = ['start']
        #imagine base route is [0, 1, 2, 3, 4]
        #reverse route is [4, 3, 2, 1, 0]
        for current_index in range(1, len(self.base_automatic_route)): #first destination is 2nd item in list
            self.in_progress_automatic_route.append(self.base_automatic_route[current_index])
        #now in progress route is ['start', 1, 2, 3, 4]

        self.in_progress_automatic_route.append('end')
        for current_index in range(1, len(reversed_base_automatic_route)):
            self.in_progress_automatic_route.append(reversed_base_automatic_route[current_index])
        #now in progress route is ['start', 1, 2, 3, 4, 'end', 3, 2, 1, 0]

    def can_follow_automatic_route(self):
        '''
        Description:
            Returns whether the next step of this unit's in-progress movement route could be completed at this moment
        Input:
            None
        Output
            boolean: Returns whether the next step of this unit's in-progress movement route could be completed at this moment
        '''
        next_step = self.in_progress_automatic_route[0]
        if next_step == 'end': #can drop off freely unless train without train station
            if not (self.is_vehicle and self.vehicle_type == 'train' and not self.images[0].current_cell.has_intact_building('train_station')):
                return(True)
            else:
                return(False)
        elif next_step == 'start':
            #ignores consumer goods
            if len(self.images[0].current_cell.tile.get_held_commodities(True)) > 0 or self.get_inventory_used() > 0: #only start round trip if there is something to deliver, either from tile or in inventory already
                if not (self.is_vehicle and self.vehicle_type == 'train' and not self.images[0].current_cell.has_intact_building('train_station')): #can pick up freely unless train without train station
                    return(True)
                else:
                    return(False)
            else:
                return(False)
        else: #must have enough movement points, not blocked
            x_change = next_step[0] - self.x
            y_change = next_step[1] - self.y
            return(self.can_move(x_change, y_change, False))

    def follow_automatic_route(self):
        '''
        Description:
            Moves along this unit's in-progress movement route until it cannot complete the next step. A unit will wait for commodities to transport from the start, then pick them up and move along the path, picking up others along
                the way. At the end of the path, it drops all commodities and moves back towards the start
        Input:
            None
        Output:
            None
        '''
        progressed = False
        
        if len(self.in_progress_automatic_route) > 0:
            while self.can_follow_automatic_route():
                next_step = self.in_progress_automatic_route[0]
                if next_step == 'start':
                    self.pick_up_all_commodities(True)
                elif next_step == 'end':
                    self.drop_inventory()
                else:
                    x_change = next_step[0] - self.x
                    y_change = next_step[1] - self.y
                    self.move(x_change, y_change)
                    if not (self.is_vehicle and self.vehicle_type == 'train' and not self.images[0].current_cell.has_intact_building('train_station')):
                        if self.get_next_automatic_stop() == 'end': #only pick up commodities on way to end
                            self.pick_up_all_commodities(True)
                progressed = True
                self.in_progress_automatic_route.append(self.in_progress_automatic_route.pop(0)) #move first item to end
                
        return(progressed) #returns whether unit did anything to show unit in movement routes report

    def get_next_automatic_stop(self):
        '''
        Description:
            Returns the next stop for this unit's in-progress automatic route, or 'none' if there are stops
        Input:
            None
        Output:
            string: Returns the next stop for this unit's in-progress automatic route, or 'none' if there are stops
        '''
        for current_stop in self.in_progress_automatic_route:
            if current_stop in ['start', 'end']:
                return(current_stop)
        return('none')

    def pick_up_all_commodities(self, ignore_consumer_goods = False):
        '''
        Description:
            Adds as many local commodities to this unit's inventory as possible, possibly choosing not to pick up consumer goods based on the inputted boolean
        Input:
            boolean ignore_consumer_goods = False: Whether to not pick up consumer goods from this unit's tile
        Output:
            None
        '''
        tile = self.images[0].current_cell.tile
        while self.get_inventory_remaining() > 0 and len(tile.get_held_commodities(ignore_consumer_goods)) > 0:
            commodity = tile.get_held_commodities(ignore_consumer_goods)[0]
            self.change_inventory(commodity, 1)
            tile.change_inventory(commodity, -1)

    def clear_automatic_route(self):
        '''
        Description:
            Removes this unit's saved automatic movement route
        Input:
            None
        Output:
            None
        '''
        self.base_automatic_route = []
        self.in_progress_automatic_route = []
        if self == self.global_manager.get('displayed_mob'):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self)

    def selection_sound(self):
        '''
        Description:
            Plays a sound when this unit is selected, with a varying sound based on this unit's type
        Input:
            None
        Output:
            None
        '''
        if self.is_officer or self.is_group or self.is_vehicle:
            if self.is_battalion or self.is_safari or (self.is_officer and self.officer_type in ['hunter', 'major']):
                self.global_manager.get('sound_manager').play_sound('bolt_action_2')
            if self.global_manager.get('current_country').name == 'France':
                possible_sounds = ['voices/french sir 1', 'voices/french sir 2', 'voices/french sir 3']
            elif self.global_manager.get('current_country').name == 'Germany':
                possible_sounds = ['voices/german sir 1', 'voices/german sir 2', 'voices/german sir 3', 'voices/german sir 4', 'voices/german sir 5']
            else:
                possible_sounds = ['voices/sir 1', 'voices/sir 2', 'voices/sir 3']
                if self.is_vehicle and self.vehicle_type == 'ship':
                    possible_sounds.append('voices/steady she goes')
            self.global_manager.get('sound_manager').play_sound(random.choice(possible_sounds))

    def set_automatically_replace(self, new_value):
        '''
        Description:
            Sets this unit's automatically replace status
        Input:
            boolean new_value: New automatically replace value
        Output:
            None
        '''
        if new_value == True and self.is_worker and self.worker_type == 'slave' and self.global_manager.get('slave_traders_strength') <= 0:
            text_utility.print_to_screen('The slave trade has been eradicated and automatic replacement of slaves is no longer possible', self.global_manager)
            return()
        self.automatically_replace = new_value
        displayed_mob = self.global_manager.get('displayed_mob')
        if self == displayed_mob:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self)
        elif (not displayed_mob == 'none') and displayed_mob.is_pmob and displayed_mob.is_group and (displayed_mob.officer == self or displayed_mob.worker == self):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), displayed_mob)

    def get_image_id_list(self, override_values={}):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        image_id_list = super().get_image_id_list(override_values)
        if (self.is_officer or self.is_group) and self.veteran:
            image_id_list.append('misc/veteran_icon.png')
        if self.sentry_mode:
            image_id_list.append('misc/sentry_icon.png')
        return(image_id_list)

    def set_sentry_mode(self, new_value):
        '''
        Description:
            Sets a new sentry mode of this status, creating a sentry icon or removing the existing one as needed
        Input:
            boolean new_value: New sentry mode status for this unit
        Output:
            None
        '''
        old_value = self.sentry_mode
        if not old_value == new_value:
            self.sentry_mode = new_value
            self.update_image_bundle()
            if new_value == True:
                self.remove_from_turn_queue()
                if self.global_manager.get('displayed_mob') == self:
                    actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self) #updates actor info display with sentry icon
            else:
                if self.movement_points > 0 and not (self.is_vehicle and self.crew == 'none'):
                    self.add_to_turn_queue()
            if self == self.global_manager.get('displayed_mob'):
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self)

    def add_to_turn_queue(self):
        '''
        Description:
            At the start of the turn or once removed from another actor/building, attempts to add this unit to the list of units to cycle through with tab. Units in sentry mode or without movement are not added
        Input:
            None
        Output:
            None
        '''
        if (not self.sentry_mode) and self.movement_points > 0 and self.end_turn_destination == 'none':
            turn_queue = self.global_manager.get('player_turn_queue')
            if not self in turn_queue:
                turn_queue.append(self)

    def remove_from_turn_queue(self):
        '''
        Description:
            Removes this unit from the list of units to cycle through with tab
        Input:
            None
        Output:
            None
        '''
        turn_queue = self.global_manager.get('player_turn_queue')
        self.global_manager.set('player_turn_queue', utility.remove_from_list(turn_queue, self))

    def replace(self):
        '''
        Description:
            Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications
        Input:
            None
        Output:
            None
        '''
        self.set_name(self.default_name)
        if (self.is_group or self.is_officer) and self.veteran:
            self.veteran = False
            for current_image in self.images:
                current_image.image.remove_member('veteran_icon')

    def manage_health_attrition(self, current_cell = 'default'): #other versions of manage_health_attrition in group, vehicle, and resource_building
        '''
        Description:
            Checks this mob for health attrition each turn
        Input:
            string/cell current_cell = 'default': Records which cell the attrition is taking place in, used when a unit is in a building or another mob and does not technically exist in any cell
        Output:
            None
        '''
        if current_cell == 'default':
            current_cell = self.images[0].current_cell
        if current_cell == 'none':
            return()
        if current_cell.local_attrition():
            transportation_minister = self.global_manager.get('current_ministers')[self.global_manager.get('type_minister_dict')['transportation']]
            if transportation_minister.no_corruption_roll(6, 'health_attrition') == 1 or self.global_manager.get('effect_manager').effect_active('boost_attrition'):
                worker_type = 'none'
                if self.is_worker:
                    worker_type = self.worker_type
                if (not worker_type in ['African', 'slave']) or random.randrange(1, 7) <= 2:
                    self.attrition_death()

    def attrition_death(self, show_notification = True):
        '''
        Description:
            Kills this unit, takes away its next turn, and automatically buys a replacement when it fails its rolls for health attrition. If an officer dies, the replacement costs the officer's usual recruitment cost and does not have
                the previous officer's experience. If a worker dies, the replacement is found and recruited from somewhere else on the map, increasing worker upkeep colony-wide as usual
        Input:
            boolean show_notification: Whether a notification should be shown for this death - depending on where this was called, a notification may have already been shown
        Output:
            None
        '''
        self.global_manager.get('evil_tracker').change(3)
        if (self.is_officer or self.is_worker) and self.automatically_replace:
            if show_notification:
                text = utility.capitalize(self.name) + ' has died from attrition at (' + str(self.x) + ', ' + str(self.y) + ') /n /n' + self.generate_attrition_replacement_text()
                self.global_manager.get('notification_manager').display_notification({
                    'message': text,
                    'zoom_destination': self.images[0].current_cell.tile,
                })

            self.temp_disable_movement()
            self.replace()
            self.death_sound('violent')
        else:
            if show_notification:
                self.global_manager.get('notification_manager').display_notification({
                    'message': utility.capitalize(self.name) + ' has died from attrition at (' + str(self.x) + ', ' + str(self.y) + ')',
                    'zoom_destination': self.images[0].current_cell.tile,
                })

            self.die()

    def generate_attrition_replacement_text(self):
        '''
        Description:
            Generates text to use in attrition replacement notifications when this unit suffers health attrition
        Input:
            None
        Output:
            Returns text to use in attrition replacement notifications
        '''
        text = 'The unit will remain inactive for the next turn as replacements are found. /n /n'
        if self.is_officer:
            text += str(self.global_manager.get('recruitment_costs')['officer']) + ' money has automatically been spent to recruit a replacement. /n /n'
        elif self.is_worker and self.worker_type == 'slave':
            text += str(self.global_manager.get('recruitment_costs')['slave workers']) + ' money has automatically been spent to purchase replacements. /n /n'
        return(text)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob and drops any commodities it is carrying
        Input:
            None
        Output:
            None
        '''
        if (not self.images[0].current_cell == 'none') and (not self.images[0].current_cell.tile == 'none'): #drop inventory on death
            current_tile = self.images[0].current_cell.tile
            for current_commodity in self.global_manager.get('commodity_types'):
                current_tile.change_inventory(current_commodity, self.get_inventory(current_commodity))
        self.remove_from_turn_queue()
        super().remove()
        self.global_manager.set('pmob_list', utility.remove_from_list(self.global_manager.get('pmob_list'), self)) #make a version of pmob_list without self and set pmob_list to it

    def draw_outline(self):
        '''
        Description:
            Draws a flashing outline around this mob if it is selected, also shows its end turn destination, if any
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('show_selection_outlines'):
            for current_image in self.images:
                if not current_image.current_cell == 'none' and self == current_image.current_cell.contained_mobs[0]: #only draw outline if on top of stack
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (current_image.outline), current_image.outline_width)

                    if len(self.base_automatic_route) > 0:
                        start_coordinates = self.base_automatic_route[0]
                        end_coordinates = self.base_automatic_route[-1]
                        for current_coordinates in self.base_automatic_route:
                            current_tile = self.grids[0].find_cell(current_coordinates[0], current_coordinates[1]).tile
                            equivalent_tile = current_tile.get_equivalent_tile()
                            if current_coordinates == start_coordinates:
                                color = 'purple'
                            elif current_coordinates == end_coordinates:
                                color = 'yellow'
                            else:
                                color = 'bright blue'
                            current_tile.draw_destination_outline(color)
                            if not equivalent_tile == 'none':
                                equivalent_tile.draw_destination_outline(color)
                    
            if (not self.end_turn_destination == 'none') and self.end_turn_destination.images[0].can_show(): #only show outline if tile is showing
                self.end_turn_destination.draw_destination_outline()
                equivalent_tile = self.end_turn_destination.get_equivalent_tile()
                if not equivalent_tile == 'none':
                    equivalent_tile.draw_destination_outline()

    def ministers_appointed(self):
        '''
        Description:
            Returns whether all ministers are appointed to do an action, otherwise prints an error message
        Input:
            None
        Output:
            boolean: Returns whether all ministers are appointed to do an action, otherwise prints an error message
        '''
        if minister_utility.positions_filled(self.global_manager): #not self.controlling_minister == 'none':
            return(True)
        else:
            text_utility.print_to_screen('', self.global_manager)
            text_utility.print_to_screen('You cannot do that until all ministers have been appointed', self.global_manager)
            text_utility.print_to_screen('Press q or the button in the upper left corner of the screen to manage your ministers', self.global_manager)
            return(False)

    def set_controlling_minister_type(self, new_type):
        '''
        Description:
            Sets the type of minister that controls this unit, like 'Minister of Trade'
        Input:
            string new_type: Type of minister to control this unit, like 'Minister of Trade'
        Output:
            None
        '''
        self.controlling_minister_type = new_type
        self.update_controlling_minister()

    def update_controlling_minister(self):
        '''
        Description:
            Sets the minister that controls this unit to the one occupying the office that has authority over this unit
        Input:
            None
        Output:
            None
        '''
        if self.controlling_minister_type == 'none':
            self.controlling_minister = 'none'
        else:
            self.controlling_minister = self.global_manager.get('current_ministers')[self.controlling_minister_type]
            for current_minister_type_image in self.global_manager.get('minister_image_list'):
                if current_minister_type_image.minister_type == self.controlling_minister_type:
                    current_minister_type_image.calibrate(self.controlling_minister)

    def end_turn_move(self):
        '''
        Description:
            If this mob has any pending movement orders at the end of the turn, this executes the movement. Currently used to move ships between Africa and Europe at the end of the turn
        Input:
            None
        Output:
            None
        '''
        if not self.end_turn_destination == 'none':
            if self.grids[0] in self.end_turn_destination.grids: #if on same grid
                nothing = 0 #do once queued movement is added
            else: #if on different grid
                if self.can_travel():
                    self.go_to_grid(self.end_turn_destination.grids[0], (self.end_turn_destination.x, self.end_turn_destination.y))
                    self.manage_inventory_attrition() #do an inventory check when crossing ocean, using the destination's terrain
            self.end_turn_destination = 'none'
    
    def can_travel(self): #if can move between Europe, Africa, etc.
        '''
        Description:
            Returns whether this mob can cross the ocean, like going between Africa and Europe. By default, mobs cannot cross the ocean, but subclasses like ship are able to return True
        Input:
            None
        Output:
            boolean: Returns True if this mob can cross the ocean, otherwise returns False
        '''
        return(False) #different for subclasses

    def change_inventory(self, commodity, change):
        '''
        Description:
            Changes the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to change the inventory of
            int change: Amount of commodities of the inputted type to add. Removes commodities of the inputted type if negative
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Description:
            Sets the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to set the inventory of
            int new_value: Amount of commodities of the inputted type to set inventory to
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self)

    def fire(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Has different effects from die in certain subclasses
        Input:
            None
        Output:
            None
        '''
        self.die('fired')

    def can_move(self, x_change, y_change, can_print = True):
        '''
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc.
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
            boolean can_print = True: Whether to print messages to explain why a unit can't move in a certain direction
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        '''
        future_x = self.x + x_change
        future_y = self.y + y_change
        transportation_minister = self.global_manager.get('current_ministers')[self.global_manager.get('type_minister_dict')['transportation']]
        if not transportation_minister == 'none':
            if self.can_leave():
                if not self.grid.is_abstract_grid:
                    if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
                        future_cell = self.grid.find_cell(future_x, future_y)
                        if future_cell.visible or self.can_explore:
                            destination_type = 'land'
                            if future_cell.terrain == 'water':
                                destination_type = 'water' #if can move to destination, possible to move onto ship in water, possible to 'move' into non-visible water while exploring
                            passed = False
                            if destination_type == 'land':
                                if self.can_walk or self.can_explore or (future_cell.has_intact_building('port') and self.images[0].current_cell.terrain == 'water'):
                                    passed = True
                            elif destination_type == 'water':
                                if destination_type == 'water':
                                    if self.can_swim or (future_cell.has_vehicle('ship', self.is_worker) and not self.is_vehicle) or (self.can_explore and not future_cell.visible) or (self.is_battalion and (not future_cell.get_best_combatant('npmob') == 'none')):
                                        passed = True
                                    elif future_cell.y > 0 and self.can_walk and not self.can_swim_river: #can move through river with maximum movement points while becoming disorganized
                                        passed = True
                            if passed:
                                if destination_type == 'water':
                                    if not (future_cell.has_vehicle('ship', self.is_worker) and not self.is_vehicle): #doesn't matter if can move in ocean or rivers if boarding ship
                                        if not (self.is_battalion and (not future_cell.get_best_combatant('npmob') == 'none')): #battalions can attack enemies in water, but must retreat afterward
                                            if (future_y == 0 and not self.can_swim_ocean) or (future_y > 0 and (not self.can_swim_river) and (not self.can_walk)):
                                                if can_print:
                                                    if future_y == 0:
                                                        text_utility.print_to_screen('This unit cannot move into the ocean.', self.global_manager)
                                                    elif future_y > 0:
                                                        text_utility.print_to_screen('This unit cannot move through rivers.', self.global_manager)
                                                return(False)
                                    
                                if self.movement_points >= self.get_movement_cost(x_change, y_change) or self.has_infinite_movement and self.movement_points > 0: #self.movement_cost:
                                    if (not future_cell.has_npmob()) or self.is_battalion or self.is_safari or (self.can_explore and not future_cell.visible): #non-battalion units can't move into enemies
                                        return(True)
                                    else:
                                        if can_print:
                                            text_utility.print_to_screen('You cannot move through enemy units.', self.global_manager)
                                        return(False)
                                else:
                                    if can_print:
                                        text_utility.print_to_screen('You do not have enough movement points to move.', self.global_manager)
                                        text_utility.print_to_screen('You have ' + str(self.movement_points) + ' movement points while ' + str(self.get_movement_cost(x_change, y_change)) + ' are required.', self.global_manager)
                                    return(False)
                            elif destination_type == 'land' and not self.can_walk: #if trying to walk on land and can't
                                if can_print:
                                    text_utility.print_to_screen('You cannot move on land with this unit unless there is a port.', self.global_manager)
                                return(False)
                            else: #if trying to swim in water and can't 
                                if can_print:
                                    text_utility.print_to_screen('You cannot move on ocean with this unit.', self.global_manager)
                                return(False)
                        else:
                            if can_print:
                                text_utility.print_to_screen('You cannot move into an unexplored tile.', self.global_manager)
                            return(False)
                    else:
                        text_utility.print_to_screen('You cannot move off of the map.', self.global_manager)
                        return(False)
                else:
                    if can_print:
                        text_utility.print_to_screen('You cannot move while in this area.', self.global_manager)
                    return(False)
        else:
            if can_print:
                text_utility.print_to_screen('You cannot move units before a Minister of Transportation has been appointed.', self.global_manager)
            return(False)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this mob's tooltip can be shown. Along with the superclass' requirements, mob tooltips cannot be shown when attached to another actor, such as when working in a building
        Input:
            None
        Output:
            None
        '''
        if self.in_vehicle or self.in_group or self.in_building:
            return(False)
        else:
            return(super().can_show_tooltip())

    def embark_vehicle(self, vehicle, focus = True):
        '''
        Description:
            Hides this mob and embarks it on the inputted vehicle as a passenger. Any commodities held by this mob are put on the vehicle if there is cargo space, or dropped in its tile if there is no cargo space
        Input:
            vehicle vehicle: vehicle that this mob becomes a passenger of
            boolean focus = False: Whether this action is being "focused on" by the player or done automatically
        Output:
            None
        '''
        self.in_vehicle = True
        self.vehicle = vehicle
        self.selected = False
        for current_commodity in self.get_held_commodities(): #gives inventory to ship
            num_held = self.get_inventory(current_commodity)
            for current_commodity_unit in range(num_held):
                if vehicle.get_inventory_remaining() > 0:
                    vehicle.change_inventory(current_commodity, 1)
                else:
                    self.images[0].current_cell.tile.change_inventory(current_commodity, 1)
        self.hide_images()
        self.remove_from_turn_queue()
        vehicle.contained_mobs.append(self)
        self.inventory_setup() #empty own inventory
        vehicle.hide_images()
        vehicle.show_images() #moves vehicle images to front
        if focus and not vehicle.initializing: #don't select vehicle if loading in at start of game
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), 'none', override_exempt=True)
            vehicle.select()
        if not self.global_manager.get('loading_save'):
            self.global_manager.get('sound_manager').play_sound('footsteps')
        self.clear_automatic_route()

    def disembark_vehicle(self, vehicle, focus = True):
        '''
        Description:
            Shows this mob and disembarks it from the inputted vehicle after being a passenger
        Input:
            vehicle vehicle: vehicle that this mob disembarks from
            boolean focus = False: Whether this action is being "focused on" by the player or done automatically
        Output:
            None
        '''
        vehicle.contained_mobs = utility.remove_from_list(vehicle.contained_mobs, self)
        self.vehicle = 'none'
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        for current_image in self.images:
            current_image.add_to_cell()
        vehicle.selected = False
        if self.images[0].current_cell.get_intact_building('port') == 'none':
            self.set_disorganized(True)
        if self.can_trade and self.can_hold_commodities: #if caravan
            consumer_goods_present = vehicle.get_inventory('consumer goods')
            if consumer_goods_present > 0:
                consumer_goods_transferred = consumer_goods_present
                if consumer_goods_transferred > self.inventory_capacity:
                    consumer_goods_transferred = self.inventory_capacity
                vehicle.change_inventory('consumer goods', -1 * consumer_goods_transferred)
                self.change_inventory('consumer goods', consumer_goods_transferred)
                text_utility.print_to_screen(utility.capitalize(self.name) + ' automatically took ' + str(consumer_goods_transferred) + ' consumer goods from ' + vehicle.name + '\'s cargo.', self.global_manager)

        self.add_to_turn_queue()
        if focus:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), 'none', override_exempt=True)
            self.select()
            if self.global_manager.get('minimap_grid') in self.grids:
                self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
            #self.update_image_bundle()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), self.images[0].current_cell.tile)
            self.global_manager.get('sound_manager').play_sound('footsteps')

    def start_construction(self, building_info_dict):
        '''
        Description
            Used when the player clicks on a construct building or train button, displays a choice notification that allows the player to construct it or not. Choosing to construct starts the construction process, costs an amount based
                on the building built, and consumes the group's movement points
        Input:
            dictionary building_info_dict: string keys corresponding to various values used to determine the building constructed
                string building_type: type of building, like 'resource'
                string building_name: name of building, like 'ivory camp'
                string attached_resource: optional, type of resource building produces, like 'ivory'
        Output:
            None
        '''
        self.building_type = building_info_dict['building_type']
        self.building_name = building_info_dict['building_name']
        if self.building_type == 'resource':
            self.attached_resource = building_info_dict['attached_resource']
        else:
            self.attached_resource = ''
        
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = 0 #construction shouldn't have critical failures
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'constructor': self, 'type': 'start construction'}
        self.global_manager.set('ongoing_action', True)
        self.global_manager.set('ongoing_action_type', 'construction')
        message = 'Are you sure you want to start constructing a ' + text_utility.remove_underscores(self.building_name) + '? /n /n'
        
        cost = actor_utility.get_building_cost(self.global_manager, self, self.building_type, self.building_name)

        message += 'The planning and materials will cost ' + str(cost) + ' money. /n /n'
        
        message += 'If successful, a ' + text_utility.remove_underscores(self.building_name) + ' will be built. ' #change to match each building
        if self.building_type == 'resource':
            message += 'A ' + text_utility.remove_underscores(self.building_name) + ' expands the tile\'s warehouse capacity, and each work crew attached to it can attempt to produce ' + self.attached_resource + ' each turn. /n /n'
            message += 'Upgrades to the ' + text_utility.remove_underscores(self.building_name) + ' can increase the maximum number of work crews attached and/or how much ' + self.attached_resource + ' each attached work crew can attempt to produce each turn. '
        elif self.building_type == 'infrastructure':
            if self.building_name == 'road':
                message += 'A road halves movement cost when moving to another tile that has a road or railroad and can later be upgraded to a railroad. '
            elif self.building_name == 'railroad':
                message += 'A railroad, like a road, halves movement cost when moving to another tile that has a road or railroad. '
                message += 'It is also required for trains to move and for a train station to be built.'
            elif self.building_name == 'road_bridge':
                message += 'A bridge built on a river tile between 2 land tiles allows movement across the river. '
                message += 'A road bridge acts as a road between the tiles it connects and can later be upgraded to a railroad bridge. '
            elif self.building_name == 'railroad_bridge':
                message += 'A bridge built on a river tile between 2 land tiles allows movement across the river. '
                message += 'A railroad bridge acts as a railroad between the tiles it connects. '
        elif self.building_type == 'port':
            message += 'A port allows steamboats and steamships to enter the tile and expands the tile\'s warehouse capacity. '
            if self.y == 1:
                message += '/n /nThis port would be adjacent to the ocean, allowing it to be used as a destination or starting point for steamships traveling between theatres. '
            else:
                message += '/n /nThis port would not be adjacent to the ocean. '
                
            if self.adjacent_to_river():
                message += '/n /nThis port would be adjacent to a river, allowing steamboats to be built there. '
            else:
                message += '/n /nThis port would not be adjacent to a river.'
        elif self.building_type == 'train_station':
            message += 'A train station is required for a train to exchange cargo and passengers, allows trains to be built, and expands the tile\'s warehouse capacity'
        elif self.building_type == 'trading_post':
            message += 'A trading post increases the likelihood that the natives of the local village will be willing to trade and reduces the risk of hostile interactions when trading.'
        elif self.building_type == 'mission':
            message += 'A mission decreases the difficulty of converting the natives of the local village and reduces the risk of hostile interactions when converting.'
        elif self.building_type == 'fort':
            message += 'A fort increases the combat effectiveness of your units standing in this tile.'
        elif self.building_type == 'train':
            message += 'A train is a unit that can carry commodities and passengers at very high speed along railroads. It can only exchange cargo and passengers at a train station. '
            message += 'It also requires an attached worker as crew to function.'
        elif self.building_type == 'steamboat':
            message += 'A steamboat is a unit that can carry commodities and passengers at high speed along rivers. '
            message += 'It also requires an attached worker as crew to function.'
        else:
            message += 'Placeholder building description'
        message += ' /n /n'
 
        self.global_manager.get('notification_manager').display_notification({
            'message': message,
            'choices': ['start construction', 'stop construction'],
            'extra_parameters': choice_info_dict
        })

    def construct(self):
        '''
        Description:
            Controls the construction process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        self.current_construction_type = 'default'
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
            
        cost = actor_utility.get_building_cost(self.global_manager, self, self.building_type, self.building_name)

        if self.building_name in ['train', 'steamboat']:
            verb = 'assemble'
            preterit_verb = 'assembled'
            noun = 'assembly'
        else:
            verb = 'construct'
            preterit_verb = 'constructed'
            noun = 'construction'

        self.global_manager.get('money_tracker').change(-1 * cost, 'construction')
        text = ''

        text += 'The ' + self.name + ' attempts to ' + verb + ' a ' + text_utility.remove_underscores(self.building_name) + '. /n /n'
        if not self.veteran:    
            self.global_manager.get('notification_manager').display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.',
                'num_dice': num_dice,
                'notification_type': 'construction'
            })
        else:
            text += ('The ' + self.officer.name + ' can roll twice and pick the higher result. /n /n')
            self.global_manager.get('notification_manager').display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.',
                'num_dice': num_dice,
                'notification_type': 'construction'
            })

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Rolling... ',
            'num_dice': num_dice,
            'notification_type': 'roll'
        })

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, cost, 'construction', 2)
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            first_roll_list = dice_utility.roll_to_list(6, noun.capitalize() + ' roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            second_roll_list = dice_utility.roll_to_list(6, 'second', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, False)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = 'CRITICAL FAILURE'
                elif i >= self.current_min_crit_success:
                    word = 'CRITICAL SUCCESS'
                elif i >= self.current_min_success:
                    word = 'SUCCESS'
                else:
                    word = 'FAILURE'
                result_outcome_dict[i] = word
            text += ('The higher result, ' + str(roll_result) + ': ' + result_outcome_dict[roll_result] + ', was used. /n')
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, cost, 'construction')
            roll_list = dice_utility.roll_to_list(6, noun.capitalize() + ' roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to continue.',
            'num_dice': num_dice,
            'notification_type': 'construction'
        })

        text += '/n'
        if roll_result >= self.current_min_success:
            text += 'The ' + self.name + ' successfully ' + preterit_verb + ' the ' + text_utility.remove_underscores(self.building_name) + '. /n'
        else:
            text += 'Little progress was made and the ' + self.officer.name + ' requests more time and funds to complete the ' + noun + ' of the ' + text_utility.remove_underscores(self.building_name) + '. /n'

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += ' /nThe ' + self.officer.name + ' managed the ' + noun + ' well enough to become a veteran. /n'
        if roll_result >= 4:
            success = True
            self.global_manager.get('notification_manager').display_notification({
                'message': text + ' /nClick to remove this notification.',
                'notification_type': 'final_construction'
            })
        else:
            success = False
            self.global_manager.get('notification_manager').display_notification({
                'message': text,
            })
        self.global_manager.set('construction_result', [self, roll_result, success, self.building_name])
        
    def complete_construction(self):
        '''
        Description:
            Used when the player finishes rolling for construction, shows the construction's results and makes any changes caused by the result. If successful, the building is constructed, promotes engineer to a veteran on critical
                success
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('construction_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.set_movement_points(0)

            input_dict = {
                'coordinates': (self.x, self.y),
                'grids': self.grids,
                'name': self.building_name,
                'modes': ['strategic'],
                'init_type': self.building_type
            }

            if not self.building_type in ['train', 'steamboat']:
                if self.images[0].current_cell.has_building(self.building_type): #if building of same type exists, remove it and replace with new one
                    self.images[0].current_cell.get_building(self.building_type).remove_complete()
            if self.building_type == 'resource':
                input_dict['image'] = self.global_manager.get('resource_building_dict')[self.attached_resource]
                input_dict['resource_type'] = self.attached_resource
            elif self.building_type == 'infrastructure':
                building_image_id = 'none'
                if self.building_name == 'road':
                    building_image_id = 'buildings/infrastructure/road.png'
                elif self.building_name == 'railroad':
                    building_image_id = 'buildings/infrastructure/railroad.png'
                else: #bridge image handled in infrastructure initialization to use correct horizontal/vertical version
                    building_image_id = 'buildings/infrastructure/road.png'
                input_dict['image'] = building_image_id
                input_dict['infrastructure_type'] = self.building_name
            elif self.building_type == 'port':
                input_dict['image'] = 'buildings/port.png'
            elif self.building_type == 'train_station':
                input_dict['image'] = 'buildings/train_station.png'
            elif self.building_type == 'trading_post':
                input_dict['image'] = 'buildings/trading_post.png'
            elif self.building_type == 'mission':
                input_dict['image'] = 'buildings/mission.png'
            elif self.building_type == 'fort':
                input_dict['image'] = 'buildings/fort.png'
            elif self.building_type == 'train':
                image_dict = {'default': 'mobs/train/default.png', 'crewed': 'mobs/train/default.png', 'uncrewed': 'mobs/train/uncrewed.png'}
                input_dict['image_dict'] = image_dict
                input_dict['crew'] = 'none'
            elif self.building_type == 'steamboat':
                image_dict = {'default': 'mobs/steamboat/default.png', 'crewed': 'mobs/steamboat/default.png', 'uncrewed': 'mobs/steamboat/uncrewed.png'}
                input_dict['image_dict'] = image_dict
                input_dict['crew'] = 'none'
                input_dict['init_type'] = 'boat'
            else:
                input_dict['image'] = 'buildings/' + self.building_type + '.png'
            new_building = self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)

            if self.building_type in ['port', 'train_station', 'resource']:
                warehouses = self.images[0].current_cell.get_building('warehouses')
                if not warehouses == 'none':
                    if warehouses.damaged:
                        warehouses.set_damaged(False)
                    warehouses.upgrade()
                else:
                    input_dict['image'] = 'misc/empty.png'
                    input_dict['name'] = 'warehouses'
                    input_dict['init_type'] = 'warehouses'
                    self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
                    
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), self.images[0].current_cell.tile) #update tile display to show new building
            if self.building_type in ['steamboat', 'train']:
                new_building.move_to_front()
                new_building.select()
            else:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self) #update mob display to show new upgrade possibilities
        self.global_manager.set('ongoing_action', False)
        self.global_manager.set('ongoing_action_type', 'none')

    def start_repair(self, building_info_dict):
        '''
        Description
            Used when the player clicks on a repair building button, displays a choice notification that allows the player to repair it or not. Choosing to repair starts the repair process, costs an amount based on the building's total
                cost with upgrades, and consumes the construction gang's movement points
        Input:
            dictionary building_info_dict: string keys corresponding to various values used to determine the building constructed
                string building_type: type of building to repair, like 'resource'
                string building_name: name of building, like 'ivory camp'
        Output:
            None
        '''
        self.building_type = building_info_dict['building_type']
        self.building_name = building_info_dict['building_name']
        self.repaired_building = self.images[0].current_cell.get_building(self.building_type)
        
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success - 1 #easier than building new building
        self.current_max_crit_fail = 0 #construction shouldn't have critical failures
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'constructor': self, 'type': 'start repair'}
        self.global_manager.set('ongoing_action', True)
        self.global_manager.set('ongoing_action_type', 'construction')
        message = 'Are you sure you want to start repairing the ' + text_utility.remove_underscores(self.building_name) + '? /n /n'
        message += 'The planning and materials will cost ' + str(self.repaired_building.get_repair_cost()) + ' money, half the initial cost of the building\'s construction. /n /n'
        message += 'If successful, the ' + text_utility.remove_underscores(self.building_name) + ' will be restored to full functionality. /n /n'
            
        self.global_manager.get('notification_manager').display_notification({
            'message': message,
            'choices': ['start repair', 'stop repair'],
            'extra_parameters': choice_info_dict
        })

    def repair(self):
        '''
        Description:
            Controls the repair process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        self.current_construction_type = 'repair'
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
        
        self.global_manager.get('money_tracker').change(self.repaired_building.get_repair_cost() * -1, 'construction')
        text = ''
        text += 'The ' + self.name + ' attempts to repair the ' + text_utility.remove_underscores(self.building_name) + '. /n /n'
        if not self.veteran:    
            self.global_manager.get('notification_manager').display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.',
                'num_dice': num_dice,
                'notification_type': 'construction'
            })
        else:
            text += ('The ' + self.officer.name + ' can roll twice and pick the higher result. /n /n')
            self.global_manager.get('notification_manager').display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.',
                'num_dice': num_dice,
                'notification_type': 'construction'
            })

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Rolling... ',
            'num_dice': num_dice,
            'notification_type': 'roll'
        })

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, self.repaired_building.get_repair_cost(), 'construction', 2)
            first_roll_list = dice_utility.roll_to_list(6, 'Construction roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            second_roll_list = dice_utility.roll_to_list(6, 'second', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, False)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = 'CRITICAL FAILURE'
                elif i >= self.current_min_crit_success:
                    word = 'CRITICAL SUCCESS'
                elif i >= self.current_min_success:
                    word = 'SUCCESS'
                else:
                    word = 'FAILURE'
                result_outcome_dict[i] = word
            text += ('The higher result, ' + str(roll_result) + ': ' + result_outcome_dict[roll_result] + ', was used. /n')
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, self.repaired_building.get_repair_cost(), 'construction')
            roll_list = dice_utility.roll_to_list(6, 'Construction roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to continue.',
            'num_dice': num_dice,
            'notification_type': 'construction'
        })
            
        text += '/n'
        if roll_result >= self.current_min_success: #3+ required on D6 for repair
            text += 'The ' + self.name + ' successfully repaired the ' + text_utility.remove_underscores(self.building_name) + '. /n'
        else:
            text += 'Little progress was made and the ' + self.officer.name + ' requests more time and funds to complete the repair. /n'

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += ' /nThe ' + self.officer.name + ' managed the construction well enough to become a veteran. /n'
        if roll_result >= 4:
            success = True
            self.global_manager.get('notification_manager').display_notification({
                'message': text + ' /nClick to remove this notification.',
                'notification_type': 'final_construction'
            })
        else:
            success = False
            self.global_manager.get('notification_manager').display_notification({
                'message': text,
            })
        self.global_manager.set('construction_result', [self, roll_result, success, self.building_name])  

    def complete_repair(self):
        '''
        Description:
            Used when the player finishes rolling for a repair, shows the repair's results and makes any changes caused by the result. If successful, the building is repaired and returned to full functionality, promotes engineer to a
                veteran on critical success
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('construction_result')[1]
        if roll_result >= self.current_min_success: #if repair succeeded
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.set_movement_points(0)
            self.repaired_building.set_damaged(False)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self) #update mob info display to hide repair button
        self.global_manager.set('ongoing_action', False)
        self.global_manager.set('ongoing_action_type', 'none')
