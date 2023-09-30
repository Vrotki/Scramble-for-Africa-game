#Contains functionality for actor display buttons

import random
from ..interface_types.buttons import button
from ..util import main_loop_utility, utility, actor_utility, minister_utility, trial_utility, text_utility, game_transitions

class embark_all_passengers_button(button):
    '''
    Button that commands a vehicle to take all other mobs in its tile as passengers
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        input_dict['button_type'] = 'embark all'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take all other mobs in its tile as passengers
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            vehicle = self.global_manager.get('displayed_mob')
            can_embark = True
            if self.vehicle_type == 'train':
                if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                    text_utility.print_to_screen('A train can only pick up passengers at a train station.', self.global_manager)
                    can_embark = False
            if can_embark:
                if vehicle.sentry_mode:
                    vehicle.set_sentry_mode(False)
                for contained_mob in vehicle.images[0].current_cell.contained_mobs:
                    passenger = contained_mob
                    if passenger.is_pmob and not passenger.is_vehicle: #vehicles and enemies won't be picked up as passengers
                        passenger.embark_vehicle(vehicle)
                self.global_manager.get('sound_manager').play_sound('voices/all aboard ' + str(random.randrange(1, 4)))
        else:
            text_utility.print_to_screen('You are busy and cannot embark all passengers.', self.global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if not displayed_mob.has_crew: #do not show if ship does not have crew
                return(False)
            if (not self.vehicle_type == displayed_mob.vehicle_type) and (not displayed_mob.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = displayed_mob.vehicle_type
                self.image.set_image('buttons/embark_' + self.vehicle_type + '_button.png')
        return(result)

class disembark_all_passengers_button(button):
    '''
    Button that commands a vehicle to eject all of its passengers
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        input_dict['button_type'] = 'disembark all'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to eject all of its passengers
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            vehicle = self.global_manager.get('displayed_mob')
            can_disembark = True
            if self.vehicle_type == 'train':
                if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                    text_utility.print_to_screen('A train can only drop off passengers at a train station.', self.global_manager)
                    can_disembark = False
            if can_disembark:
                if vehicle.sentry_mode:
                    vehicle.set_sentry_mode(False)
                if len(vehicle.contained_mobs) > 0:
                    vehicle.contained_mobs[-1].selection_sound()
                vehicle.eject_passengers()
        else:
            text_utility.print_to_screen('You are busy and cannot disembark all passengers.', self.global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            vehicle = self.global_manager.get('displayed_mob')
            if not vehicle.has_crew: #do not show if ship does not have crew
                return(False)
            if (not self.vehicle_type == vehicle.vehicle_type) and (not vehicle.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = vehicle.vehicle_type
                self.image.set_image('buttons/disembark_' + self.vehicle_type + '_button.png')
        return(result)

class enable_sentry_mode_button(button):
    '''
    Button that enables sentry mode for a unit, causing it to not be added to the turn cycle queue
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'enable sentry mode'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is not already in sentry mode, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if not displayed_mob.is_pmob:
                return(False)
            elif displayed_mob.sentry_mode:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button activates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):   
            displayed_mob = self.global_manager.get('displayed_mob')      
            displayed_mob.set_sentry_mode(True)
            if (self.global_manager.get('effect_manager').effect_active('promote_on_sentry') 
            and (displayed_mob.is_group or displayed_mob.is_officer) 
            and not displayed_mob.veteran): #purely for promotion testing, not normal functionality
                displayed_mob.promote()
        else:
            text_utility.print_to_screen('You are busy and cannot enable sentry mode.', self.global_manager)

class disable_sentry_mode_button(button):
    '''
    Button that disables sentry mode for a unit, causing it to not be added to the turn cycle queue
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'disable sentry mode'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is in sentry mode, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if not displayed_mob.is_pmob:
                return(False)
            elif not displayed_mob.sentry_mode:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button deactivates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = self.global_manager.get('displayed_mob')     
            displayed_mob.set_sentry_mode(False)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), displayed_mob)
        else:
            text_utility.print_to_screen('You are busy and cannot disable sentry mode.', self.global_manager)

class enable_automatic_replacement_button(button):
    '''
    Button that enables automatic attrition replacement for a unit or one of its components
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'target_type': string value - Type of unit/subunit targeted by this button, such as 'unit', 'officer', or 'worker'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.target_type = input_dict['target_type']
        input_dict['button_type'] = 'enable automatic replacement'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the targeted unit component is present and does not already have automatic replacement, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if not displayed_mob.is_pmob:
                return(False)
            elif displayed_mob.is_vehicle:
                return(False)
            elif displayed_mob.is_group and self.target_type == 'unit':
                return(False)
            elif (not displayed_mob.is_group) and (not self.target_type == 'unit'):
                return(False)
            elif ((self.target_type == 'unit' and displayed_mob.automatically_replace) or 
                (self.target_type == 'worker' and displayed_mob.worker.automatically_replace) or 
                (self.target_type == 'officer' and displayed_mob.officer.automatically_replace)):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button enables automatic replacement for the selected unit
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):     
            displayed_mob = self.global_manager.get('displayed_mob')    
            if self.target_type == 'unit':
                target = displayed_mob
            elif self.target_type == 'worker':
                target = displayed_mob.worker
            elif self.target_type == 'officer':
                target = displayed_mob.officer         
            target.set_automatically_replace(True)
        else:
            text_utility.print_to_screen('You are busy and cannot enable automatic replacement.', self.global_manager)

class disable_automatic_replacement_button(button):
    '''
    Button that disables automatic attrition replacement for a unit or one of its components
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'target_type': string value - Type of unit/subunit targeted by this button, such as 'unit', 'officer', or 'worker'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.target_type = input_dict['target_type']
        input_dict['button_type'] = 'disable automatic replacement'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the targeted unit component is present and has automatic replacement, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if not displayed_mob.is_pmob:
                return(False)
            elif displayed_mob.is_vehicle:
                return(False)
            elif displayed_mob.is_group and self.target_type == 'unit':
                return(False)
            elif (not displayed_mob.is_group) and (not self.target_type == 'unit'):
                return(False)
            elif ((self.target_type == 'unit' and not displayed_mob.automatically_replace) or 
                (self.target_type == 'worker' and not displayed_mob.worker.automatically_replace) or 
                (self.target_type == 'officer' and not displayed_mob.officer.automatically_replace)):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disables automatic replacement for the selected unit
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = self.global_manager.get('displayed_mob')
            if self.target_type == 'unit':
                target = displayed_mob
            elif self.target_type == 'worker':
                target = displayed_mob.worker
            elif self.target_type == 'officer':
                target = displayed_mob.officer         
            target.set_automatically_replace(False)
        else:
            text_utility.print_to_screen('You are busy and cannot disable automatic replacement.', self.global_manager)

class end_unit_turn_button(button):
    '''
    Button that ends a unit's turn, removing it from the current turn's turn cycle queue
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'end unit turn'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob in the turn queue, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if not displayed_mob.is_pmob:
                return(False)
            elif not displayed_mob in self.global_manager.get('player_turn_queue'):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected unit from the current turn's turn cycle queue
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            self.global_manager.get('displayed_mob').remove_from_turn_queue()
            game_transitions.cycle_player_turn(self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot end this unit\'s turn.', self.global_manager)

class remove_work_crew_button(button):
    '''
    Button that removes a work crew from a building
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
                'building_type': Type of building to remove workers from, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = input_dict['building_type']
        input_dict['button_type'] = 'remove worker'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding work crew to remove, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_building:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes a work crew from a building
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):         
            self.attached_label.attached_list[self.attached_label.list_index].leave_building(self.attached_label.actor.cell.contained_buildings[self.building_type])
        else:
            text_utility.print_to_screen('You are busy and cannot remove a work crew from a building.', self.global_manager)

class disembark_vehicle_button(button):
    '''
    Button that disembarks a passenger from a vehicle
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        input_dict['button_type'] = 'disembark'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding passenger to disembark, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_vehicle:
                return(False)
            old_vehicle_type = self.vehicle_type
            self.vehicle_type = self.attached_label.actor.vehicle_type
            if not self.vehicle_type == old_vehicle_type and not self.vehicle_type == 'none': #if changed
                self.image.set_image('buttons/disembark_' + self.vehicle_type + '_button.png')
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disembarks a passenger from a vehicle
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):         
            if len(self.attached_label.actor.contained_mobs) > 0:
                can_disembark = True
                if self.vehicle_type == 'train':
                    if self.attached_label.actor.images[0].current_cell.contained_buildings['train_station'] == 'none':
                        text_utility.print_to_screen('A train can only drop off passengers at a train station.', self.global_manager)
                        can_disembark = False
                if can_disembark:
                    passenger = self.attached_label.attached_list[self.attached_label.list_index]
                    if passenger.sentry_mode:
                        passenger.set_sentry_mode(False)
                    passenger.selection_sound()
                    self.attached_label.attached_list[self.attached_label.list_index].disembark_vehicle(self.attached_label.actor)
            else:
                text_utility.print_to_screen('You must select a ' + self.vehicle_type + 'with passengers to disembark passengers.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot disembark from a ' + self.vehicle_type + '.', self.global_manager)

class embark_vehicle_button(button):
    '''
    Button that commands a selected mob to embark a vehicle of the correct type in the same tile
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'vehicle_type': string value - Type of vehicle this button embarks, like 'train' or 'ship'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = input_dict['vehicle_type']
        self.was_showing = False
        input_dict['button_type'] = 'embark'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob cannot embark vehicles or if there is no vehicle in the tile to embark, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if not displayed_mob.is_pmob:
                result = False
            elif displayed_mob.in_vehicle or displayed_mob.is_vehicle:
                result = False
            elif not displayed_mob.actor_type == 'minister' and not displayed_mob.images[0].current_cell.has_vehicle(self.vehicle_type):
                result = False
        if not result == self.was_showing: #if visibility changes, update actor info display
            self.was_showing = result
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), displayed_mob)
        self.was_showing = result
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a selected mob to embark a vehicle of the correct type in the same tile
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = self.global_manager.get('displayed_mob')
            if displayed_mob.images[0].current_cell.has_vehicle(self.vehicle_type):
                vehicle = displayed_mob.images[0].current_cell.get_vehicle(self.vehicle_type)
                rider = displayed_mob
                can_embark = True
                if vehicle.vehicle_type == 'train':
                    if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                        text_utility.print_to_screen('A train can only pick up passengers at a train station.', self.global_manager)
                        can_embark = False
                if can_embark:
                    if rider.sentry_mode:
                        rider.set_sentry_mode(False)
                    if vehicle.sentry_mode:
                        vehicle.set_sentry_mode(False)
                    rider.embark_vehicle(vehicle)
                    self.global_manager.get('sound_manager').play_sound('voices/all aboard ' + str(random.randrange(1, 4)))
            else:
                text_utility.print_to_screen('You must select a unit in the same tile as a crewed ' + self.vehicle_type + ' to embark.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot embark a ' + self.vehicle_type + '.', self.global_manager)

class cycle_passengers_button(button):
    '''
    Button that cycles the order of passengers displayed in a vehicle
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        input_dict['button_type'] = 'cycle passengers'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a vehicle or if the vehicle does not have enough passengers to cycle through, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if not displayed_mob.is_vehicle:
                return(False)
            elif not len(displayed_mob.contained_mobs) > 3: #only show if vehicle with 3+ passengers
                return(False)
            self.vehicle_type = displayed_mob.vehicle_type
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of passengers displayed in a vehicle
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = self.global_manager.get('displayed_mob')
            moved_mob = displayed_mob.contained_mobs.pop(0)
            displayed_mob.contained_mobs.append(moved_mob)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), displayed_mob) #updates mob info display list to show changed passenger order
        else:
            text_utility.print_to_screen('You are busy and cannot cycle passengers.', self.global_manager)

class cycle_work_crews_button(button):
    '''
    Button that cycles the order of work crews in a building
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.previous_showing_result = False
        input_dict['button_type'] = 'cycle work crews'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile's cell has a resource building containing more than 3 work crews, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_tile = self.global_manager.get('displayed_tile')
            if displayed_tile.cell.contained_buildings['resource'] == 'none':
                self.previous_showing_result = False
                return(False)
            elif not len(displayed_tile.cell.contained_buildings['resource'].contained_work_crews) > 3: #only show if building with 3+ work crews
                self.previous_showing_result = False
                return(False)
        if self.previous_showing_result == False and result == True:
            self.previous_showing_result = result
            self.attached_label.set_label(self.attached_label.message) #update label to update this button's location
        self.previous_showing_result = result
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of work crews displayed in a building
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_tile = self.global_manager.get('displayed_tile')
            moved_mob = displayed_tile.cell.contained_buildings['resource'].contained_work_crews.pop(0)
            displayed_tile.cell.contained_buildings['resource'].contained_work_crews.append(moved_mob)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), displayed_tile) #updates tile info display list to show changed work crew order
        else:
            text_utility.print_to_screen('You are busy and cannot cycle work crews.', self.global_manager)

class work_crew_to_building_button(button):
    '''
    Button that commands a work crew to work in a certain type of building in its tile
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'building_type': string value - Type of buliding this button attaches workers to, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = input_dict['building_type']
        self.attached_work_crew = 'none'
        self.attached_building = 'none'
        input_dict['button_type'] = 'worker to resource'
        super().__init__(input_dict, global_manager)

    def update_info(self):
        '''
        Description:
            Updates the building this button assigns workers to depending on the buildings present in this tile
        Input:
            None
        Output:
            None
        '''
        self.attached_work_crew = self.global_manager.get('displayed_mob')
        if self.attached_work_crew != 'none' and self.attached_work_crew.is_work_crew:
            self.attached_building = self.attached_work_crew.images[0].current_cell.get_intact_building(self.building_type)
        else:
            self.attached_building = 'none'
    
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a work crew, otherwise returns same as superclass
        '''
        self.update_info()
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.attached_work_crew != 'none' and self.attached_work_crew.is_work_crew)
    
    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the building it assigns workers to
        Input:
            None
        Output:
            None
        '''
        if not (self.attached_work_crew == 'none' or self.attached_building == 'none'):
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected work crew to the ' + self.attached_building.name + ', producing ' + self.attached_building.resource_type + ' over time.'])
            else:
                self.set_tooltip(['placeholder'])
        elif not self.attached_work_crew == 'none':
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected work crew to a resource building, producing commodities over time.'])
        else:
            self.set_tooltip(['placeholder'])

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a work crew to work in a certain type of building in its tile
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if not self.attached_building == 'none':
                if self.attached_building.scale > len(self.attached_building.contained_work_crews): #if has extra space
                    if self.attached_work_crew.sentry_mode:
                        self.attached_work_crew.set_sentry_mode(False)
                    self.attached_work_crew.work_building(self.attached_building)
                else:
                    text_utility.print_to_screen('This building is at its work crew capacity.', self.global_manager)
                    text_utility.print_to_screen('Upgrade the building\'s scale to increase work crew capacity.', self.global_manager)
            else:
                text_utility.print_to_screen('This work crew must be in the same tile as a resource production building to work in it', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot attach a work crew to a building.', self.global_manager)
            

class trade_button(button):
    '''
    Button that commands a caravan to trade with a village
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'trade'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of trading, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').can_trade)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a caravan to trade with a village
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = self.global_manager.get('displayed_mob')
            if current_mob.movement_points >= 1:
                if self.global_manager.get('money') >= self.global_manager.get('action_prices')['trade']:
                    current_cell = current_mob.images[0].current_cell
                    if current_cell.has_building('village'):
                        if current_cell.get_building('village').population > 0:
                            if current_mob.get_inventory('consumer goods') > 0:
                                if minister_utility.positions_filled(self.global_manager):
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    current_mob.start_trade()
                                else:
                                    text_utility.print_to_screen('You cannot do any actions until all ministers have been appointed.', self.global_manager)
                            else:
                                text_utility.print_to_screen('Trading requires at least 1 unit of consumer goods.', self.global_manager)
                        else:
                            text_utility.print_to_screen('Trading is only possible in a village with population above 0.', self.global_manager)
                    else:
                        text_utility.print_to_screen('Trading is only possible in a village.', self.global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['trade']) + ' money needed to trade with a village.', self.global_manager)
            else:
                text_utility.print_to_screen('Trading requires all remaining movement points, at least 1', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot trade.', self.global_manager)

class convert_button(button):
    '''
    Button that commands missionaries to convert a native village
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'f
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'convert'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a group of missionaries, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').can_convert)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands missionaries to convert a native village
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = self.global_manager.get('displayed_mob')
            if current_mob.movement_points >= 1:
                if self.global_manager.get('money') >= self.global_manager.get('action_prices')['conversion']:
                    current_cell = current_mob.images[0].current_cell
                    if current_cell.has_building('village'):
                        if current_cell.get_building('village').aggressiveness > 1:
                            if current_cell.get_building('village').population > 0:
                                if current_mob.ministers_appointed():
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    current_mob.start_converting()
                            else:
                                text_utility.print_to_screen('This village has no population and cannot be converted.', self.global_manager)
                        else:
                            text_utility.print_to_screen('This village already has the minimum aggressiveness and cannot be converted.', self.global_manager)
                    else:
                        text_utility.print_to_screen('Converting is only possible in a village.', self.global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['conversion']) + ' money needed to attempt to convert the natives.', self.global_manager)
            else:
                text_utility.print_to_screen('Converting requires all remaining movement points, at least 1.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot convert.', self.global_manager)

class rumor_search_button(button):
    '''
    Button that commands an expedition to search a village for rumors of the location of a lore mission artifact
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'rumor search'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an expedition, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').can_explore)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands missionaries to convert a native village
        Input:
            None
        Output:
            None
        '''
        if not self.global_manager.get('current_lore_mission') == 'none':
            if main_loop_utility.action_possible(self.global_manager):
                current_mob = self.global_manager.get('displayed_mob')
                if current_mob.movement_points >= 1:
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')['rumor_search']:
                        current_cell = current_mob.images[0].current_cell
                        if current_cell.has_building('village'):
                            if current_cell.get_building('village').population > 0:
                                if not self.global_manager.get('current_lore_mission').confirmed_all_locations_revealed:
                                    if not current_cell.get_building('village').found_rumors:
                                        if current_mob.ministers_appointed():
                                            if current_mob.sentry_mode:
                                                current_mob.set_sentry_mode(False)
                                            current_mob.start_rumor_search()
                                    else:
                                        text_utility.print_to_screen('This village\'s rumors regarding the location of the ' + self.global_manager.get('current_lore_mission').name + ' have already been found.', self.global_manager)
                                else:
                                    text_utility.print_to_screen('All possible locations of the ' + self.global_manager.get('current_lore_mission').name + ' have already been revealed.', self.global_manager)
                            else:
                                text_utility.print_to_screen('This village has no population and no rumors can be found.', self.global_manager)
                        else:
                            text_utility.print_to_screen('Searching for rumors is only possible in a village.', self.global_manager)
                    else:
                        text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['rumor_search']) + ' money needed to attempt a rumor search.', self.global_manager)
                else:
                    text_utility.print_to_screen('A rumor search requires all remaining movement points, at least 1.', self.global_manager)
            else:
                text_utility.print_to_screen('You are busy and cannot search for rumors.', self.global_manager)
        else:
            text_utility.print_to_screen('There are no ongoing lore missions for which to find rumors.', self.global_manager)

class artifact_search_button(button):
    '''
    Button that commands an expedition to search a rumored location for a lore mission artifact
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'artifact search'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an expedition, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').can_explore)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands missionaries to convert a native village
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('current_lore_mission') != 'none':
            if main_loop_utility.action_possible(self.global_manager):
                current_mob = self.global_manager.get('displayed_mob')
                if current_mob.movement_points >= 1:
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')['artifact_search']:
                        if self.global_manager.get('current_lore_mission').has_revealed_possible_artifact_location(current_mob.x, current_mob.y):
                            if current_mob.ministers_appointed():
                                if current_mob.sentry_mode:
                                    current_mob.set_sentry_mode(False)
                                current_mob.start_artifact_search()
                        else:
                            text_utility.print_to_screen('You have not found any rumors indicating that the ' + self.global_manager.get('current_lore_mission').name + ' may be at this location.', self.global_manager)
                    else:
                        text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['artifact_search']) + ' money needed to attempt a artifact search.', self.global_manager)
                else:
                    text_utility.print_to_screen('An artifact search requires all remaining movement points, at least 1.', self.global_manager)
            else:
                text_utility.print_to_screen('You are busy and cannot search for artifact.', self.global_manager)
        else:
            text_utility.print_to_screen('There are no ongoing lore missions for which to find artifacts.', self.global_manager)

class capture_slaves_button(button):
    '''
    Button that commands a battalion to capture slaves from a village
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'capture slaves'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a group of missionaries, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').is_battalion)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a battalion to capture slaves from a native village
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = self.global_manager.get('displayed_mob')
            if current_mob.movement_points >= 1:
                if self.global_manager.get('money') >= self.global_manager.get('action_prices')['slave_capture']:
                    current_cell = current_mob.images[0].current_cell
                    if current_cell.has_building('village'):
                        if current_cell.get_building('village').population > 0:
                            if current_mob.ministers_appointed():
                                if current_mob.sentry_mode:
                                    current_mob.set_sentry_mode(False)
                                current_mob.start_capture_slaves()
                        else:
                            text_utility.print_to_screen('This village has no remaining population to be captured.', self.global_manager)
                    else:
                        text_utility.print_to_screen('Capturing slaves is only possible in a village.', self.global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['slave_capture']) + ' money needed to attempt to capture slaves.', self.global_manager)
            else:
                text_utility.print_to_screen('Capturing slaves requires all remaining movement points, at least 1.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot capture slaves.', self.global_manager)

class take_loan_button(button):
    '''
    Button that commands a merchant to start a loan search in Europe
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'take loan'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a merchant, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').is_officer and self.global_manager.get('displayed_mob').officer_type == 'merchant')

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a merchant to start a loan search
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = self.global_manager.get('displayed_mob')
            if self.global_manager.get('europe_grid') in current_mob.grids:
                if current_mob.movement_points >= 1:
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')['loan']:
                        if current_mob.ministers_appointed():
                            if current_mob.sentry_mode:
                                current_mob.set_sentry_mode(False)
                            current_mob.start_loan_search()
                    else:
                        text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['loan_search']) + ' money needed to search for a loan offer.', self.global_manager)
                else:
                    text_utility.print_to_screen('Searching for a loan offer requires all remaining movement points, at least 1.', self.global_manager)
            else:
                text_utility.print_to_screen('A merchant can only search for a loan while in Europe', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot search for a loan offer.', self.global_manager)

class labor_broker_button(button):
    '''
    Buttons that commands a vehicle without crew or an officer to use a labor broker in a port to recruit a worker from a nearby village, with a price based on the village's aggressiveness and distance
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'labor broker'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an officer, a steamship, or a non-steamship vehicle without crew, otherwise returns same as superclass
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_mob = self.global_manager.get('displayed_mob')
            if displayed_mob.is_officer and displayed_mob.officer_type != 'evangelist':
                return(True)
            elif displayed_mob.is_vehicle and not (displayed_mob.can_swim_ocean or displayed_mob.has_crew):
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands an officer or vehicle without crew to use a labor broker in a port
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = self.global_manager.get('displayed_mob')
            if self.global_manager.get('strategic_map_grid') in current_mob.grids:
                if current_mob.images[0].current_cell.has_intact_building('port'):
                    cost_info_list = self.get_cost()
                    if not cost_info_list == 'none':
                        if current_mob.movement_points >= 1:
                            if self.global_manager.get('money_tracker').get() >= cost_info_list[1]:
                                if current_mob.ministers_appointed():
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    choice_info_dict = {'recruitment_type': 'African worker labor broker', 'cost': cost_info_list[1], 'mob_image_id': 'mobs/African worker/default.png', 'type': 'recruitment',
                                        'source_type': 'labor broker', 'village': cost_info_list[0]}
                                    self.global_manager.get('actor_creation_manager').display_recruitment_choice_notification(choice_info_dict, 'African workers', self.global_manager)
                            else:
                                text_utility.print_to_screen('You cannot afford the recruitment cost of ' + str(cost_info_list[1]) + ' for the cheapest available worker. ', self.global_manager)
                        else:
                            text_utility.print_to_screen('Using a labor broker requires all remaining movement points, at least 1.', self.global_manager)
                    else:
                        text_utility.print_to_screen('There are no eligible villages to recruit workers from.', self.global_manager)
                else:
                    text_utility.print_to_screen('A labor broker can only be used at a port.', self.global_manager)
            else:
                text_utility.print_to_screen('A labor broker can only be used at a port.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot use a labor broker.', self.global_manager)

    def get_cost(self):
        '''
        Description:
            Calculates and returns the cost of using a labor broker in a port at the currently selected unit's location, based on nearby villages' aggressiveness and distance from the port
        Input:
            None
        Output:
            string/list: If no valid villages are found, returns 'none'. Otherwise, returns a list with the village as the first item and the cost as the second item
        '''
        lowest_cost_village = 'none'
        lowest_cost = 0
        for current_village in self.global_manager.get('village_list'):
            if current_village.population > 0:
                distance = int(utility.find_object_distance(current_village, self.global_manager.get('displayed_mob')))
                cost = (5 * current_village.aggressiveness) + distance
                if cost < lowest_cost or lowest_cost_village == 'none':
                    lowest_cost_village = current_village
                    lowest_cost = cost
        if lowest_cost_village == 'none':
            return('none')
        else:
            return([lowest_cost_village, lowest_cost])

class track_beasts_button(button):
    '''
    Button that orders a safari to spend 1 movement point to attempt to reveal beasts in its tile and adjacent explored tiles
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'track beasts'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a safari, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').is_group and self.global_manager.get('displayed_mob').is_safari)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a safari to attempt to track beasts
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = self.global_manager.get('displayed_mob')
            if self.global_manager.get('strategic_map_grid') in current_mob.grids:
                if current_mob.movement_points >= 1:
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')['track_beasts']:
                        if current_mob.ministers_appointed():
                            if current_mob.sentry_mode:
                                current_mob.set_sentry_mode(False)
                            current_mob.track_beasts()
                    else:
                        text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['track_beasts']) + ' money needed to search for a loan offer.', self.global_manager)
                else:
                    text_utility.print_to_screen('Tracking beasts requires 1 movement point.', self.global_manager)
            else:
                text_utility.print_to_screen('A safari can only track beasts in Africa', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot track beasts.', self.global_manager)

class switch_theatre_button(button):
    '''
    Button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A destination is chosen when the player clicks a tile in another theatre.
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'switch theatre'
        super().__init__(input_dict, global_manager)

    def on_click(self):      
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A
                destination is chosen when the player clicks a tile in another theatre.
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = self.global_manager.get('displayed_mob')
            if current_mob.movement_points >= 1:
                if not (self.global_manager.get('strategic_map_grid') in current_mob.grids and (current_mob.y > 1 or (current_mob.y == 1 and not current_mob.images[0].current_cell.has_intact_building('port')))): #can leave if in ocean or if in coastal port
                    if current_mob.can_leave(): #not current_mob.grids[0] in self.destination_grids and
                        if current_mob.sentry_mode:
                            current_mob.set_sentry_mode(False)
                        if not self.global_manager.get('current_game_mode') == 'strategic':
                            game_transitions.set_game_mode('strategic', self.global_manager)
                            current_mob.select()
                        current_mob.clear_automatic_route()
                        current_mob.end_turn_destination = 'none'
                        self.global_manager.set('choosing_destination', True)
                        self.global_manager.set('choosing_destination_info_dict', {'chooser': current_mob}) #, 'destination_grids': self.destination_grids
                else:
                    text_utility.print_to_screen('You are inland and cannot cross the ocean.', self.global_manager) 
            else:
                text_utility.print_to_screen('Crossing the ocean requires all remaining movement points, at least 1.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot move.', self.global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of traveling between theatres, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').is_pmob and self.global_manager.get('displayed_mob').can_travel())

class build_train_button(button):
    '''
    Button that commands a construction gang to assemble a train at a train station
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'build train'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of constructing buildings, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').can_construct)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a construction gang to assemble a train at a train station
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = self.global_manager.get('displayed_mob')
            if displayed_mob.movement_points >= 1:
                cost = actor_utility.get_building_cost(self.global_manager, displayed_mob, 'train')
                if self.global_manager.get('money') >= cost:
                    if not self.global_manager.get('europe_grid') in displayed_mob.grids:
                        if not displayed_mob.images[0].current_cell.terrain == 'water':
                            if displayed_mob.images[0].current_cell.has_intact_building('train_station'):
                                if displayed_mob.ministers_appointed():
                                    if displayed_mob.sentry_mode:
                                        displayed_mob.set_sentry_mode(False)
                                    self.construct()
                            else:
                                text_utility.print_to_screen('A train can only be assembled on a train station.', self.global_manager)
                        else:
                            text_utility.print_to_screen('A train can only be assembled on a train station.', self.global_manager)
                    else:
                        text_utility.print_to_screen('A train can only be assembled on a train station.', self.global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(cost) + ' money needed to assemble a train.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have enough movement points to assemble a train.', self.global_manager)
                text_utility.print_to_screen('You have ' + str(displayed_mob.movement_points) + ' movement points while 1 is required.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot build a train.', self.global_manager)

    def construct(self):
        '''
        Description:
            Commands the selected mob to construct a train
        Input:
            None
        Output:
            None
        '''
        building_info_dict = {}
        building_info_dict['building_type'] = 'train'
        building_info_dict['building_name'] = 'train'
        self.global_manager.get('displayed_mob').start_construction(building_info_dict)

class build_steamboat_button(button):
    '''
    Button that commands a construction gang to assemble a steammboat at a port
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'build steamboat'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of constructing buildings, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.global_manager.get('displayed_mob').can_construct)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a construction gang to assemble a steamboat at a port
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = self.global_manager.get('displayed_mob')
            if displayed_mob.movement_points >= 1:
                cost = actor_utility.get_building_cost(self.global_manager, displayed_mob, 'steamboat')
                if self.global_manager.get('money') >= cost:
                    if not self.global_manager.get('europe_grid') in displayed_mob.grids:
                        if not displayed_mob.images[0].current_cell.terrain == 'water':
                            if displayed_mob.images[0].current_cell.has_intact_building('port'):
                                if displayed_mob.adjacent_to_river():
                                    if displayed_mob.ministers_appointed():
                                        if displayed_mob.sentry_mode:
                                            displayed_mob.set_sentry_mode(False)
                                        self.construct()
                                else:
                                    text_utility.print_to_screen('A steamboat assembled here would not be able to access any rivers.', self.global_manager)
                            else:
                                text_utility.print_to_screen('A steamboat can only be assembled on a port.', self.global_manager)
                        else:
                            text_utility.print_to_screen('A steamboat can only be assembled on a port.', self.global_manager)
                    else:
                        text_utility.print_to_screen('A steamboat can only be assembled on a port.', self.global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(cost) + ' money needed to assemble a steamboat.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have enough movement points to assemble a steamboat.', self.global_manager)
                text_utility.print_to_screen('You have ' + str(displayed_mob.movement_points) + ' movement points while 1 is required.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot build a train.', self.global_manager)

    def construct(self):
        '''
        Description:
            Commands the selected mob to construct a steamboat
        Input:
            None
        Output:
            None
        '''
        building_info_dict = {}
        building_info_dict['building_type'] = 'steamboat'
        building_info_dict['building_name'] = 'steamboat'
        self.global_manager.get('displayed_mob').start_construction(building_info_dict)

class construction_button(button):
    '''
    Button that commands a group to construct a certain type of building
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'building_type': Type of building built by this button, like 'resource'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = input_dict['building_type']
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.building_name = 'none'
        self.requirement = 'can_construct'
        if self.building_type == 'resource':
            self.attached_resource = 'none'
            input_dict['image_id'] = global_manager.get('resource_building_button_dict')['none']
        elif self.building_type == 'port':
            input_dict['image_id'] = 'buildings/buttons/port.png'
            self.building_name = 'port'
        elif self.building_type == 'infrastructure':
            self.road_image_id = 'buildings/buttons/road.png'
            self.railroad_image_id = 'buildings/buttons/railroad.png'
            self.road_bridge_image_id = 'buildings/buttons/road_bridge.png'
            self.railroad_bridge_image_id = 'buildings/buttons/railroad_bridge.png'
            input_dict['image_id'] = self.road_image_id
        elif self.building_type == 'train_station':
            input_dict['image_id'] = 'buildings/buttons/train_station.png'
            self.building_name = 'train station'
        elif self.building_type == 'trading_post':
            input_dict['image_id'] = 'buildings/buttons/trading_post.png'
            self.building_name = 'trading post'
            self.requirement = 'can_trade'
        elif self.building_type == 'mission':
            input_dict['image_id'] = 'buildings/buttons/mission.png'
            self.building_name = 'mission'
            self.requirement = 'can_convert'
        elif self.building_type == 'fort':
            input_dict['image_id'] = 'buildings/buttons/fort.png'
            self.building_name = 'fort'
            self.requirement = 'is_battalion'
        else:
            input_dict['image_id'] = 'buttons/default_button.png'
        input_dict['button_type'] = 'construction'
        super().__init__(input_dict, global_manager)

    def update_info(self):
        '''
        Description:
            Updates the exact kind of building constructed by this button depending on what is in the selected mob's tile, like building a road or upgrading a previously constructed road to a railroad
        Input:
            None
        Output:
            None
        '''
        self.attached_mob = self.global_manager.get('displayed_mob')
        if self.attached_mob != 'none' and self.attached_mob.images[0].current_cell != 'none':
            self.attached_tile = self.attached_mob.images[0].current_cell.tile
            if self.attached_mob.can_construct:
                if self.building_type == 'resource':
                    if self.attached_tile.cell.resource in self.global_manager.get('collectable_resources'):
                        self.attached_resource = self.attached_tile.cell.resource
                        self.image.set_image(self.global_manager.get('resource_building_button_dict')[self.attached_resource])
                        if self.attached_resource in ['gold', 'iron', 'copper', 'diamond']:
                            self.building_name = self.attached_resource + ' mine'
                        elif self.attached_resource in ['exotic wood', 'fruit', 'rubber', 'coffee']:
                            self.building_name = self.attached_resource + ' plantation'
                        elif self.attached_resource == 'ivory':
                            self.building_name = 'ivory camp'
                    else:
                        self.attached_resource = 'none'
                        self.building_name = 'none'
                        self.image.set_image(self.global_manager.get('resource_building_button_dict')['none'])
                elif self.building_type == 'infrastructure':
                    current_infrastructure = self.attached_tile.cell.contained_buildings['infrastructure']
                    if current_infrastructure == 'none':
                        if self.attached_tile.cell.terrain == 'water' and self.attached_tile.cell.y > 0:
                            self.building_name = 'road_bridge'
                            self.image.set_image('buildings/buttons/road_bridge.png')
                        else:
                            self.building_name = 'road'
                            self.image.set_image('buildings/buttons/road.png')
                    else: #if has existing infrastrucutre, show railroad version
                        if self.attached_tile.cell.terrain == 'water' and self.attached_tile.cell.y > 0:
                            self.building_name = 'railroad_bridge'
                            self.image.set_image('buildings/buttons/railroad_bridge.png')
                        else:
                            self.building_name = 'railroad'
                            self.image.set_image('buildings/buttons/railroad.png')

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of constructing the building that this button constructs, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            self.update_info()
            can_create = 'none'
            displayed_mob = self.global_manager.get('displayed_mob')
            if self.requirement == 'can_construct':
                can_create = displayed_mob.can_construct
            elif self.requirement == 'can_trade':
                can_create = displayed_mob.can_trade
            elif self.requirement == 'can_convert':
                can_create = displayed_mob.can_convert
            elif self.requirement == 'is_battalion':
                can_create = displayed_mob.is_battalion
            if not can_create: #show if unit selected can create this building
                return(False)
            if not self.attached_tile == 'none':
                if self.attached_tile.cell.has_building(self.building_type) and not self.building_type == 'infrastructure': #if building already present, do not show
                    return(False)
        return(result) 

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the type of building it constructs
        Input:
            None
        Output:
            None
        '''
        message = []
        if self.building_type == 'resource':
            if self.attached_resource == 'none':
                message.append('Builds a resource production facility to which work crews can attach to produces commodities over time.')
                message.append('Can only be built in the same tile as a resource.')
            else:
                message.append('Builds a ' + self.building_name + ' to which work crews can attach to produce ' + self.attached_resource + ' over time')
                message.append('Can only be built in the same tile as a ' + self.attached_resource + ' resource.')

        elif self.building_type == 'port':
            message.append('Builds a port, allowing steamships and steamboats to enter this tile')
            message.append('Can only be built adjacent to water')

        elif self.building_type == 'train_station':
            message.append('Builds a train station, allowing trains to pick up and drop off passengers and cargo')
            message.append('Can only be built on a railroad')
            
        elif self.building_type == 'infrastructure':
            if self.building_name == 'railroad':
                message.append('Upgrades this tile\'s road into a railroad, allowing trains to move through this tile')
                message.append('Retains the benefits of a road')
                message.append('This button can build a bridge on a river tile, build a road, or upgrade an existing road or road bridge to a railroad version')
            elif self.building_name == 'road':
                message.append('Builds a road, halving the cost to move between this tile and other tiles with roads or railroads')
                message.append('A road can be upgraded into a railroad that allows trains to move through this tile')
                message.append('This button can build a bridge on a river tile or upgrade an existing road or road bridge to a railroad version')
            elif self.building_name == 'railroad_bridge':
                message.append('Upgrades this tile\'s road bridge into a railroad bridge, allowing trains to move through this tile')
                message.append('Retains the benefits of a road bridge')
                message.append('This button can build a bridge on a river tile, build a road, or upgrade an existing road to a railroad')
            elif self.building_name == 'road_bridge':
                message.append('Builds a road bridge, allowing normal movement between the tiles it connects')
                message.append('A road bridge can be upgraded into a railroad bridge that allows trains to move through this tile')
                message.append('This button can build a road or upgrade an existing road or road bridge to a railroad version')
            else:
                self.set_tooltip(message) #Can't get building cost without road/railroad type
                return()
                
        elif self.building_type == 'trading_post':
            message.append('Builds a trading post, increasing the success chance and reducing the risk when caravans trade with the attached village')
            message.append('Can only be built in a village')
            
        elif self.building_type == 'mission':
            message.append('Builds a mission, increasing the success chance and reducing the risk when missionaries convert the attached village')
            message.append('Can only be built in a village')

        elif self.building_type == 'fort':
            message.append('Builds a fort, increasing the combat effectiveness of your units standing in this tile')
    
        else:
            message.append('placeholder')

        if self.building_type in ['train_station', 'port', 'resource']:
            message.append('Also upgrades this tile\'s warehouses by 9 inventory capacity, or creates new warehouses if none are present')
        
        base_cost = actor_utility.get_building_cost(self.global_manager, 'none', self.building_type, self.building_name)
        cost = actor_utility.get_building_cost(self.global_manager, self.attached_mob, self.building_type, self.building_name)
        
        message.append('Attempting to build costs ' + str(cost) + ' money and all remaining movement points, at least 1')
        if self.building_type in ['train', 'steamboat']:
            message.append('Unlike buildings, the cost of vehicle assembly is not impacted by local terrain')
            
        if (not self.attached_mob == 'none') and self.global_manager.get('strategic_map_grid') in self.attached_mob.grids:
            terrain = self.attached_mob.images[0].current_cell.terrain
            message.append(utility.generate_capitalized_article(self.building_name) + text_utility.remove_underscores(self.building_name) + ' ' + utility.conjugate('cost', self.building_name) + ' ' + str(base_cost) + ' money by default, which is multiplied by ' + str(self.global_manager.get('terrain_build_cost_multiplier_dict')[terrain]) + ' when built in ' + terrain + ' terrain')
        self.set_tooltip(message)
        

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a mob to construct a certain type of building
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.attached_mob.movement_points >= 1:
                cost = actor_utility.get_building_cost(self.global_manager, self.attached_mob, self.building_type, self.building_name)
                if self.global_manager.get('money') >= cost:
                    current_building = self.attached_tile.cell.get_building(self.building_type)
                    if current_building == 'none' or (self.building_name in ['railroad', 'railroad_bridge'] and current_building.is_road): #able to upgrade to railroad even though road is present, later add this to all upgradable buildings
                        if self.global_manager.get('strategic_map_grid') in self.attached_mob.grids:
                            if self.building_name in ['road_bridge', 'railroad_bridge'] or not self.attached_tile.cell.terrain == 'water':
                                displayed_mob = self.global_manager.get('displayed_mob')
                                if displayed_mob.ministers_appointed():
                                    if self.building_type == 'resource':
                                        if not self.attached_resource == 'none':
                                            if displayed_mob.sentry_mode:
                                                displayed_mob.set_sentry_mode(False)
                                            self.construct()
                                        else:
                                            text_utility.print_to_screen('This building can only be built in tiles with resources.', self.global_manager)
                                    elif self.building_type == 'port':
                                        if self.attached_mob.adjacent_to_water():
                                            if not self.attached_mob.images[0].current_cell.terrain == 'water':
                                                if displayed_mob.sentry_mode:
                                                    displayed_mob.set_sentry_mode(False)
                                                self.construct()
                                        else:
                                            text_utility.print_to_screen('This building can only be built in tiles adjacent to discovered water.', self.global_manager)
                                    elif self.building_type == 'train_station':
                                        if self.attached_tile.cell.has_intact_building('railroad'):
                                            if displayed_mob.sentry_mode:
                                                displayed_mob.set_sentry_mode(False)
                                            self.construct()
                                        else:
                                            text_utility.print_to_screen('This building can only be built on railroads.', self.global_manager)
                                    elif self.building_type == 'trading_post' or self.building_type == 'mission':
                                        if self.attached_tile.cell.has_building('village'):
                                            if displayed_mob.sentry_mode:
                                                displayed_mob.set_sentry_mode(False)
                                            self.construct()
                                        else:
                                            text_utility.print_to_screen('This building can only be built in villages.', self.global_manager)
                                    elif self.building_type == 'infrastructure' and self.building_name in ['road_bridge', 'railroad_bridge']:
                                        passed = False
                                        if self.attached_tile.cell.terrain == 'water' and self.attached_tile.cell.y > 0: #if in river tile
                                            up_cell = self.attached_tile.cell.grid.find_cell(self.attached_tile.cell.x, self.attached_tile.cell.y + 1)
                                            down_cell = self.attached_tile.cell.grid.find_cell(self.attached_tile.cell.x, self.attached_tile.cell.y - 1)
                                            left_cell = self.attached_tile.cell.grid.find_cell(self.attached_tile.cell.x - 1, self.attached_tile.cell.y)
                                            right_cell = self.attached_tile.cell.grid.find_cell(self.attached_tile.cell.x + 1, self.attached_tile.cell.y)
                                            if (not (up_cell == 'none' or down_cell == 'none')) and (not (up_cell.terrain == 'water' or down_cell.terrain == 'water')): #if vertical bridge
                                                if up_cell.visible and down_cell.visible:
                                                    passed = True
                                            elif (not (left_cell == 'none' or right_cell == 'none')) and (not (left_cell.terrain == 'water' or right_cell.terrain == 'water')): #if horizontal bridge
                                                if left_cell.visible and down_cell.visible:
                                                    passed = True
                                        if passed:
                                            if displayed_mob.sentry_mode:
                                                displayed_mob.set_sentry_mode(False)
                                            self.construct()
                                        else:
                                            text_utility.print_to_screen('A bridge can only be built on a river tile between 2 discovered land tiles', self.global_manager)

                                    else:
                                        if displayed_mob.sentry_mode:
                                            displayed_mob.set_sentry_mode(False)
                                        self.construct()
                            else:
                                text_utility.print_to_screen('This building cannot be built in water.', self.global_manager)
                        else:
                            text_utility.print_to_screen('This building can only be built in Africa.', self.global_manager)
                    else:
                        if self.building_type == 'infrastructure': #if railroad
                            text_utility.print_to_screen('This tile already contains a railroad.', self.global_manager)
                        else:
                            text_utility.print_to_screen('This tile already contains a ' + self.building_type + ' building.', self.global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(cost) + ' money needed to attempt to build a ' + self.building_name + '.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have enough movement points to construct a building.', self.global_manager)
                text_utility.print_to_screen('You have ' + str(self.attached_mob.movement_points) + ' movement points while 1 is required.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot start construction.', self.global_manager)
            
    def construct(self):
        '''
        Description:
            Commands the selected mob to construct a certain type of building, depending on this button's building_type
        Input:
            None
        Output:
            None
        '''
        building_info_dict = {}
        building_info_dict['building_type'] = self.building_type
        building_info_dict['building_name'] = self.building_name
        if self.building_type == 'resource':
            building_info_dict['attached_resource'] = self.attached_resource
        self.attached_mob.start_construction(building_info_dict)

class repair_button(button):
    '''
    Button that commands a group to repair a certain type of building
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'building_type': string value - Type of building built by this button, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = input_dict['building_type']
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.building_name = 'none'
        self.requirement = 'can_construct'
        input_dict['image_id'] = 'buildings/buttons/repair_' + self.building_type + '.png'
        if self.building_type == 'resource':
            self.attached_resource = 'none'
        else:
            self.building_name = text_utility.remove_underscores(self.building_type)
            if self.building_type == 'trading_post':
                self.requirement = 'can_trade'
            elif self.building_type == 'mission':
                self.requirement = 'can_convert'
            elif self.building_type == 'fort':
                self.requirement = 'is_battalion'
            else:
                self.requirement = 'none'
        input_dict['button_type'] = 'construction'
        super().__init__(input_dict, global_manager)

    def update_info(self):
        '''
        Description:
            If this is a resource production building repair button, updates the button's description based on the type of resource production building in the current tile
        Input:
            None
        Output:
            None
        '''
        self.attached_mob = self.global_manager.get('displayed_mob')
        if self.building_type == 'resource':
            if (not self.attached_mob == 'none') and (not self.attached_mob.images[0].current_cell == 'none'):
                self.attached_tile = self.attached_mob.images[0].current_cell.tile
                if self.attached_mob.can_construct:
                    if self.attached_tile.cell.resource in self.global_manager.get('collectable_resources'):
                        self.attached_resource = self.attached_tile.cell.resource
                        if self.attached_resource in ['gold', 'iron', 'copper', 'diamond']:
                            self.building_name = self.attached_resource + ' mine'
                        elif self.attached_resource in ['exotic wood', 'fruit', 'rubber', 'coffee']:
                            self.building_name = self.attached_resource + ' plantation'
                        elif self.attached_resource == 'ivory':
                            self.building_name = 'ivory camp'
                    else:
                        self.attached_resource = 'none'
                        self.building_name = 'none'
        else:
            if (not self.attached_mob == 'none') and (not self.attached_mob.images[0].current_cell == 'none'):
                self.attached_tile = self.attached_mob.images[0].current_cell.tile
                self.building_name = self.building_type

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of repairing this button's building, otherwise returns same as superclass. A group can repair a building if it is able to build it, and construction gang's can
                repair any type of building
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = self.global_manager.get('displayed_mob')
            if displayed_mob.can_construct or (displayed_mob.can_trade and self.requirement == 'can_trade') or (displayed_mob.can_convert and self.requirement == 'can_convert') or (displayed_mob.is_battalion and self.requirement == 'is_battalion'):
                #construction gangs can repair all buildings, caravans can only repair trading posts, missionaries can only repair missions, battalions can only repair forts
                attached_building = displayed_mob.images[0].current_cell.get_building(self.building_type)
                if (not attached_building == 'none') and attached_building.damaged:
                    self.update_info()
                    return(result)
        return(False) 

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the type of building it repairs
        Input:
            None
        Output:
            None
        '''
        message = []
        if self.showing:
            message.append('Attempts to repair the ' + text_utility.remove_underscores(self.building_name) + ' in this tile, restoring it to full functionality')
            if self.building_type in ['port', 'train_station', 'resource']:
                message.append('If successful, also automatically repairs this tile\'s warehouses')
            message.append('Attempting to repair costs ' + str(self.attached_tile.cell.get_building(self.building_type).get_repair_cost()) + ' money and all remaining movement points, at least 1')
        self.set_tooltip(message)  

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a mob to repair a certain type of building
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.attached_mob.movement_points >= 1:
                attached_building = self.attached_mob.images[0].current_cell.get_building(self.building_type)
                cost = attached_building.get_repair_cost()
                if self.global_manager.get('money') >= cost: #self.global_manager.get('building_prices')[self.building_type] / 2:
                    if self.attached_mob.sentry_mode:
                        self.attached_mob.set_sentry_mode(False)
                    self.repair()
                else:
                    text_utility.print_to_screen('You do not have the ' + str(cost) + ' money needed to attempt to repair the ' + text_utility.remove_underscores(self.building_name) + '.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have enough movement points to repair a building.', self.global_manager)
                text_utility.print_to_screen('You have ' + str(self.attached_mob.movement_points) + ' movement points while 1 is required.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot start construction.', self.global_manager)
            
    def repair(self):
        '''
        Description:
            Commands the selected mob to repair a certain type of building, depending on this button's building_type
        Input:
            None
        Output:
            None
        '''
        building_info_dict = {}
        building_info_dict['building_type'] = self.building_type
        building_info_dict['building_name'] = self.building_name
        if self.building_type == 'resource':
            building_info_dict['attached_resource'] = self.attached_resource
        self.attached_mob.start_repair(building_info_dict)

class upgrade_button(button):
    '''
    Button that commands a construction gang to upgrade a certain aspect of a building
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'base_building_type': string value - Type of building upgraded by ths button, like 'resource building'
                'upgrade_type': string value - Aspect of building upgraded by this button, like 'scale' or 'efficiency'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.base_building_type = input_dict['base_building_type']
        self.upgrade_type = input_dict['upgrade_type']
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.attached_building = 'none'
        input_dict['image_id'] = 'buttons/upgrade_' + self.upgrade_type + '_button.png'
        input_dict['button_type'] = 'construction'
        super().__init__(input_dict, global_manager)

    def update_info(self):
        '''
        Description:
            Updates which building object is attached to this button based on the selected construction gang's location relative to buildings of this button's base building type
        Input:
            None
        Output:
            None
        '''
        self.attached_building = 'none'
        self.attached_mob = self.global_manager.get('displayed_mob')
        if (not self.attached_mob == 'none') and (not self.attached_mob.images[0].current_cell == 'none'):
            self.attached_tile = self.attached_mob.images[0].current_cell.tile
            if self.attached_mob.can_construct:
                if not self.attached_tile.cell.contained_buildings[self.base_building_type] == 'none':
                    self.attached_building = self.attached_tile.cell.get_intact_building(self.base_building_type) #contained_buildings[self.base_building_type]

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of upgrading buildings or if there is no valid building in its tile to upgrade, otherwise returns same as superclass
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            self.update_info()
            return(self.global_manager.get('displayed_mob').can_construct and self.attached_building != 'none' and self.attached_building.can_upgrade(self.upgrade_type))
        return(False)

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on its attached building and the aspect it upgrades
        Input:
            None
        Output:
            None
        '''
        message = []
        if not self.attached_building == 'none':
            if self.upgrade_type == 'scale':
                message.append('Increases the maximum number of work crews that can be attached to this ' + self.attached_building.name + ' from ' + str(self.attached_building.scale) + ' to ' + str(self.attached_building.scale + 1) + '.')
            elif self.upgrade_type == 'efficiency':
                message.append('Increases the number of ' + self.attached_building.resource_type + ' production attempts made by work crews attached to this ' + self.attached_building.name + ' from ' + str(self.attached_building.efficiency) + ' to ' + str(self.attached_building.efficiency + 1) + ' per turn.')
            elif self.upgrade_type == 'warehouse_level':
                message.append('Increases the level of this tile\'s warehouses from ' + str(self.attached_building.warehouse_level) + ' to ' + str(self.attached_building.warehouse_level + 1) + ', increasing inventory capacity by 9')
            else:
                message.append('placeholder')
            message.append('Attempting to upgrade costs ' + str(self.attached_building.get_upgrade_cost()) + ' money and increases with each future upgrade to this building.')
            message.append('Unlike new buildings, the cost of building upgrades is not impacted by local terrain')
        self.set_tooltip(message)
        

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a construction gang to upgrade part of a certain building in its tile
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.attached_mob.movement_points >= 1:
                if self.global_manager.get('money') >= self.attached_building.get_upgrade_cost():
                    if self.global_manager.get('displayed_mob').ministers_appointed():
                        if self.attached_mob.sentry_mode:
                            self.attached_mob.set_sentry_mode(False)        
                        building_info_dict = {}
                        building_info_dict['upgrade_type'] = self.upgrade_type
                        building_info_dict['building_name'] = self.attached_building.name
                        building_info_dict['upgraded_building'] = self.attached_building
                        self.attached_mob.start_upgrade(building_info_dict)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(self.attached_building.get_upgrade_cost()) + ' money needed to upgrade this building.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have enough movement points to upgrade a building.', self.global_manager)
                text_utility.print_to_screen('You have ' + str(self.attached_mob.movement_points) + ' movement points while 1 is required.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot start upgrading.', self.global_manager)

class appoint_minister_button(button):
    '''
    Button that appoints the selected minister to the office corresponding to this button
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'appoint_type': string value - Office appointed to by this button, like 'Minister of Trade'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.appoint_type = input_dict['appoint_type']
        input_dict['button_type'] = 'appoint minister'
        input_dict['modes'] = ['ministers']
        input_dict['image_id'] = 'ministers/icons/' + global_manager.get('minister_type_dict')[self.appoint_type] + '.png'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the minister office that this button is attached to is open, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = self.global_manager.get('displayed_minister')
            if (not displayed_minister == 'none') and displayed_minister.current_position == 'none': #if there is an available minister displayed
                if self.global_manager.get('current_ministers')[self.appoint_type] == 'none': #if the position that this button appoints is available
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button appoints the selected minister to the office corresponding to this button
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            appointed_minister = self.global_manager.get('displayed_minister')
            if not appointed_minister.just_removed:
                appointed_minister.respond('first hired')
            appointed_minister.appoint(self.appoint_type)
            minister_utility.calibrate_minister_info_display(self.global_manager, appointed_minister)
        else:
            text_utility.print_to_screen('You are busy and cannot appoint a minister.', self.global_manager)

class remove_minister_button(button):
    '''
    Button that removes the selected minister from their current office
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'remove minister'
        input_dict['modes'] = ['ministers']
        input_dict['image_id'] = 'buttons/remove_minister_button.png'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the selected minister is currently in an office, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = self.global_manager.get('displayed_minister')
            if (not displayed_minister == 'none') and (not displayed_minister.current_position == 'none'): #if there is an available minister displayed
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected minister from their current office, returning them to the pool of available
                ministers
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            appointed_minister = self.global_manager.get('displayed_minister')
            public_opinion_penalty = appointed_minister.status_number
            text = 'Are you sure you want to remove ' + appointed_minister.name + ' from office? If removed, he will return to the pool of available ministers and be available to reappoint until the end of the turn. /n /n.'
            text += 'Removing ' + appointed_minister.name + ' from office would incur a small public opinion penalty of ' + str(public_opinion_penalty) + ', even if he were reappointed. /n /n'
            text += appointed_minister.name + ' would expect to be reappointed to a different position by the end of the turn, and would be fired permanently and incur a much larger public opinion penalty if not reappointed. /n /n'
            if appointed_minister.status_number >= 3:
                if appointed_minister.status_number == 4:
                    text += appointed_minister.name + ' is of extremely high social status, and firing him would cause a national outrage. /n /n'
                else:
                    text += appointed_minister.name + ' is of high social status, and firing him would reflect particularly poorly on your company. /n /n'
            elif appointed_minister.status_number == 1:
                text += appointed_minister.name + ' is of low social status, and firing him would have a relatively minimal impact on your company\'s reputation. /n /n'
            self.global_manager.get('notification_manager').display_notification({
                'message': text,
                'choices': ['confirm remove minister', 'none']
            })
        else:
            text_utility.print_to_screen('You are busy and cannot remove a minister.', self.global_manager)

class to_trial_button(button):
    '''
    Button that goes to the trial screen to remove the selected minister from their current office
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'to trial'
        input_dict['modes'] = input_dict['attached_label'].modes
        input_dict['image_id'] = 'buttons/to_trial_button.png'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a non-prosecutor minister with an office to be removed from is selected
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = self.global_manager.get('displayed_minister')
            if (not displayed_minister == 'none') and (not displayed_minister.current_position in ['none', 'Prosecutor']): #if there is an available non-prosecutor minister displayed
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button goes to the trial screen to remove the selected minister from the game and confiscate a portion of their
                stolen money
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.global_manager.get('money') >= self.global_manager.get('action_prices')['trial']:
                if minister_utility.positions_filled(self.global_manager):
                    if len(self.global_manager.get('minister_list')) > 8: #if any available appointees
                        defense = self.global_manager.get('displayed_minister')
                        prosecution = self.global_manager.get('current_ministers')['Prosecutor']
                        game_transitions.set_game_mode('trial', self.global_manager)
                        minister_utility.trial_setup(defense, prosecution, self.global_manager) #sets up defense and prosecution displays
                    else:
                        text_utility.print_to_screen('There are currently no available appointees to replace this minister in the event of a successful trial.', self.global_manager)
                else:
                    text_utility.print_to_screen('You have not yet appointed a minister in each office.', self.global_manager)
                    text_utility.print_to_screen('Press Q to view the minister interface.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['trial']) + ' money needed to start a trial.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot start a trial.', self.global_manager)

class active_investigation_button(button):
    '''
    Button that starts an active investigation on a minister
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'active investigation'
        input_dict['modes'] = ['ministers']
        input_dict['image_id'] = 'buttons/fabricate_evidence_button.png'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a non-prosecutor minister with an office to be removed from is selected
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = self.global_manager.get('displayed_minister')
            if displayed_minister != 'none' and displayed_minister.current_position != 'Prosecutor':
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button goes to the trial screen to remove the selected minister from the game and confiscate a portion of their
                stolen money
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.global_manager.get('money') >= self.global_manager.get('action_prices')['active_investigation']:
                if minister_utility.positions_filled(self.global_manager):
                    cost = self.global_manager.get('action_prices')['active_investigation']
                    self.global_manager.get('money_tracker').change(-1 * cost, 'active_investigation')
                    self.global_manager.get('displayed_minister').attempt_active_investigation(self.global_manager.get('current_ministers')['Prosecutor'], cost)
                    actor_utility.double_action_price(self.global_manager, 'active_investigation')
                else:
                    text_utility.print_to_screen('You have not yet appointed a minister in each office.', self.global_manager)
                    text_utility.print_to_screen('Press Q to view the minister interface.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['active_investigation']) + ' money needed to start an active investigation.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot start an active investigation.', self.global_manager)

class fabricate_evidence_button(button):
    '''
    Button in the trial screen that fabricates evidence to use against the defense in the current trial. Fabricated evidence disappears at the end of the trial or at the end of the turn
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'fabricate evidence'
        input_dict['modes'] = ['trial', 'ministers']
        input_dict['image_id'] = 'buttons/fabricate_evidence_button.png'
        super().__init__(input_dict, global_manager)

    def get_cost(self):
        '''
        Description:
            Returns the cost of fabricating another piece of evidence. The cost increases for each existing fabricated evidence against the selected minister
        Input:
            None
        Output:
            Returns the cost of fabricating another piece of evidence
        '''
        defense = self.global_manager.get('displayed_defense')
        return(trial_utility.get_fabricated_evidence_cost(defense.fabricated_evidence))

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to fabricate a piece of evidence against the selected minister
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.global_manager.get('money') >= self.get_cost():
                self.global_manager.get('money_tracker').change(-1 * self.get_cost(), 'trial')
                defense = self.global_manager.get('displayed_defense')
                prosecutor = self.global_manager.get('displayed_prosecution')
                prosecutor.display_message(prosecutor.current_position + ' ' + prosecutor.name + ' reports that evidence has been successfully fabricated for ' + str(self.get_cost()) +
                    ' money. /n /nEach new fabricated evidence will cost twice as much as the last, and fabricated evidence becomes useless at the end of the turn or after it is used in a trial. /n /n')
                defense.fabricated_evidence += 1
                defense.corruption_evidence += 1
                minister_utility.calibrate_trial_info_display(self.global_manager, self.global_manager.get('defense_info_display'), defense) #updates trial display with new evidence
            else:
                text_utility.print_to_screen('You do not have the ' + str(self.get_cost()) + ' money needed to fabricate evidence.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot fabricate evidence.', self.global_manager)

class bribe_judge_button(button):
    '''
    Button in the trial screen that bribes the judge to get an advantage in the next trial this turn
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'bribe judge'
        input_dict['modes'] = ['trial']
        input_dict['image_id'] = 'buttons/bribe_judge_button.png'
        super().__init__(input_dict, global_manager)

    def get_cost(self):
        '''
        Description:
            Returns the cost of bribing the judge, which is as much as the first piece of fabricated evidence
        Input:
            None
        Output:
            Returns the cost of bribing the judge
        '''
        return(trial_utility.get_fabricated_evidence_cost(0)) #costs as much as 1st piece of fabricated evidence

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if judge has not been bribed yet, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if not self.global_manager.get('prosecution_bribed_judge'):
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to bribe the judge
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.global_manager.get('money') >= self.get_cost():
                if not self.global_manager.get('prosecution_bribed_judge'):
                    self.global_manager.get('money_tracker').change(-1 * self.get_cost(), 'trial')
                    self.global_manager.set('prosecution_bribed_judge', True)
                    prosecutor = self.global_manager.get('displayed_prosecution')
                    prosecutor.display_message(prosecutor.current_position + ' ' + prosecutor.name + ' reports that the judge has been successfully bribed for ' + str(self.get_cost()) +
                        ' money. /n /nThis may provide a bonus in the next trial this turn. /n /n')
                else:
                    text_utility.print_to_screen('The judge has already been bribed for this trial.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have the ' + str(self.get_cost()) + ' money needed to bribe the judge.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot fabricate evidence.', self.global_manager)  
    
class hire_african_workers_button(button):
    '''
    Button that hires available workers from the displayed village/slum
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'hire_source_type': string value - Type of location workers are hired from, like 'village' or 'slums'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.hire_source_type = input_dict['hire_source_type']
        if self.hire_source_type == 'village':
            input_dict['button_type'] = 'hire village worker'
        elif self.hire_source_type == 'slums':
            input_dict['button_type'] = 'hire slums worker'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a village/slum with available workers is displayed, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if not self.global_manager.get('displayed_tile') == 'none':
                if self.hire_source_type == 'village':
                    attached_village = self.global_manager.get('displayed_tile').cell.get_building('village')
                    if not attached_village == 'none':
                        if attached_village.can_recruit_worker():
                            return(True)
                elif self.hire_source_type == 'slums':
                    attached_slums = self.global_manager.get('displayed_tile').cell.contained_buildings['slums']
                    if not attached_slums == 'none':
                        return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button hires an available worker from the displayed village/slum
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            choice_info_dict = {'recruitment_type': 'African worker ' + self.hire_source_type, 'cost': 0, 'mob_image_id': 'mobs/African worker/default.png', 'type': 'recruitment', 'source_type': self.hire_source_type}
            self.global_manager.get('actor_creation_manager').display_recruitment_choice_notification(choice_info_dict, 'African workers', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot hire a worker.', self.global_manager)

class buy_slaves_button(button):
    '''
    Button that buys slaves from slave traders
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'buy slaves'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile is in the slave traders grid, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if not self.global_manager.get('displayed_tile') == 'none':
                if self.global_manager.get('displayed_tile').cell.grid == self.global_manager.get('slave_traders_grid'):
                    if self.global_manager.get('slave_traders_strength') > 0:
                        return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button buys slaves from slave traders
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            self.cost = self.global_manager.get('recruitment_costs')['slave workers']
            if self.global_manager.get('money_tracker').get() >= self.cost:
                choice_info_dict = {'recruitment_type': 'slave workers', 'cost': self.cost, 'mob_image_id': 'mobs/slave workers/default.png', 'type': 'recruitment'}
                self.global_manager.get('actor_creation_manager').display_recruitment_choice_notification(choice_info_dict, 'slave workers', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have enough money to buy slaves.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot buy slaves.', self.global_manager)

class automatic_route_button(button):
    '''
    Button that modifies a unit's automatic movement route, with an effect depending on the button's type
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'button_type': string value - Determines the function of this button, like 'clear automatic route', 'follow automatic route', or 'draw automatic route'
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn. All automatic route buttons can only appear if the selected unit is porters or a crewed vehicle. Additionally, clear and follow automatic route buttons require that an automatic
                route already exists
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            attached_mob = self.global_manager.get('displayed_mob')
            if attached_mob.inventory_capacity > 0 and (not (attached_mob.is_group and attached_mob.can_trade)) and (not (attached_mob.is_vehicle and attached_mob.crew == 'none')):
                if self.button_type in ['clear automatic route', 'follow automatic route']:
                    if len(attached_mob.base_automatic_route) > 0:
                        return(True)
                else:
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. Clear automatic route buttons remove the selected unit's automatic route. Draw automatic route buttons enter the route
            drawing mode, in which the player can click on consecutive tiles to add them to the route. Follow automatic route buttons command the selected unit to execute its in-progress automatic route, stopping when it cannot
            continue the route for any reason
        Input:
            None
        Output:
            None
        '''
        attached_mob = self.global_manager.get('displayed_mob')
        if main_loop_utility.action_possible(self.global_manager):
            if self.global_manager.get('strategic_map_grid') in attached_mob.grids:
                if self.button_type == 'clear automatic route':
                    attached_mob.clear_automatic_route()
                    
                elif self.button_type == 'draw automatic route':
                    if attached_mob.is_vehicle and attached_mob.vehicle_type == 'train' and not attached_mob.images[0].current_cell.has_intact_building('train_station'):
                        text_utility.print_to_screen('A train can only start a movement route from a train station.', self.global_manager)
                        return()
                    attached_mob.clear_automatic_route()
                    attached_mob.add_to_automatic_route((attached_mob.x, attached_mob.y))
                    self.global_manager.set('drawing_automatic_route', True)
                    
                elif self.button_type == 'follow automatic route':
                    if attached_mob.can_follow_automatic_route():
                        attached_mob.follow_automatic_route()
                        attached_mob.remove_from_turn_queue()
                        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), attached_mob) #updates mob info display if automatic route changed anything
                    else:
                        text_utility.print_to_screen('This unit is currently not able to progress along its designated route.', self.global_manager)
            else:
                text_utility.print_to_screen('You can only create movement routes in Africa.', self.global_manager)
        else:
            if self.button_type == 'follow automatic route':
                text_utility.print_to_screen('You are busy and cannot move this unit.', self.global_manager)
            else:
                text_utility.print_to_screen('You are busy and cannot modify this unit\'s movement route.', self.global_manager)
