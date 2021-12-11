#Contains functionality for officer units
import random

from .mobs import mob
from .tiles import veteran_icon
from . import actor_utility
from . import utility
from . import notification_tools
from . import text_tools
from . import market_tools
from . import dice_utility
from . import dice
from . import scaling

class officer(mob):
    '''
    Mob that is considered an officer and can join groups and become a veteran
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
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'officer_type': string value - Type of officer that this is, like 'explorer', or 'engineer'
                'end_turn_destination': string or int tuple - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'veteran': boolean value - Required if from save, whether this officer is a veteran
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        global_manager.get('officer_list').append(self)
        self.veteran_icons = []
        self.is_officer = True
        self.officer_type = input_dict['officer_type']
        self.set_controlling_minister_type(self.global_manager.get('officer_minister_dict')[self.officer_type])
        if not from_save:
            self.veteran = False
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_officer changing
        else:
            self.veteran = input_dict['veteran']
            if self.veteran:
                self.load_veteran()

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'init_type': string value - Represents the type of actor this is, used to initialize the correct type of object on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'modes': string list value - Game modes during which this actor's images can appear
                'grid_type': string value - String matching the global manager key of this actor's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': string/string dictionary value - Version of this actor's inventory dictionary only containing commodity types with 1+ units held
                'end_turn_destination': string or int tuple - 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - How many movement points this actor currently has
                'image': File path to the image used by this object
                'officer_type': Type of officer that this is, like 'explorer' or 'engineer'
                'veteran': Whether this officer is a veteran
        '''
        save_dict = super().to_save_dict()
        save_dict['officer_type'] = self.officer_type
        save_dict['veteran'] = self.veteran
        return(save_dict)

    def promote(self):
        '''
        Description:
            Promotes this officer to a veteran after performing various actions particularly well, improving the officer's future capabilities. Creates a veteran star icon that follows this officer
        Input:
            None
        Output:
            None
        '''
        self.veteran = True
        self.set_name("veteran " + self.name)
        for current_grid in self.grids:
            if current_grid == self.global_manager.get('minimap_grid'):
                veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
            elif current_grid == self.global_manager.get('europe_grid'):
                veteran_icon_x, veteran_icon_y = (0, 0)
            else:
                veteran_icon_x, veteran_icon_y = (self.x, self.y)
            input_dict = {}
            input_dict['coordinates'] = (veteran_icon_x, veteran_icon_y)
            input_dict['grid'] = current_grid
            input_dict['image'] = 'misc/veteran_icon.png'
            input_dict['name'] = 'veteran icon'
            input_dict['modes'] = ['strategic', 'europe']
            input_dict['show_terrain'] = False
            input_dict['actor'] = self 
            self.veteran_icons.append(veteran_icon(False, input_dict, self.global_manager))
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates actor info display with veteran icon

    def load_veteran(self):
        '''
        Description:
            Promotes this officer to a veteran while loading, changing the name as needed to prevent the word veteran from being added multiple times
        Input:
            None
        Output:
            None
        '''
        name = self.name
        self.promote()
        self.set_name(name)
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Description:
            Links this officer to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean and when an officer that was previously attached to another actor becomes independent and
                visible, like when an explorer leaves an expedition. Also moves veteran icons to follow this officer
        Input:
            grid new_grid: grid that this officer is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        '''
        if self.veteran and not self.in_group: #if (not (self.in_group or self.in_vehicle)) and self.veteran:
            for current_veteran_icon in self.veteran_icons:
                current_veteran_icon.remove()
        self.veteran_icons = []
        super().go_to_grid(new_grid, new_coordinates)
        if self.veteran and not self.in_group: #if (not (self.in_group or self.in_vehicle)) and self.veteran:
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                elif current_grid == self.global_manager.get('europe_grid'):
                    veteran_icon_x, veteran_icon_y = (0, 0)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                input_dict = {}
                input_dict['coordinates'] = (veteran_icon_x, veteran_icon_y)
                input_dict['grid'] = current_grid
                input_dict['image'] = 'misc/veteran_icon.png'
                input_dict['name'] = 'veteran icon'
                input_dict['modes'] = ['strategic', 'europe']
                input_dict['show_terrain'] = False
                input_dict['actor'] = self 
                self.veteran_icons.append(veteran_icon(False, input_dict, self.global_manager))

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this officer's tooltip can be shown. Along with the superclass' requirements, officer tooltips can not be shown when attached to another actor, such as when part of a group
        Input:
            None
        Output:
            None
        '''
        if not (self.in_group or self.in_vehicle):
            return(super().can_show_tooltip())
        else:
            return(False)

    def join_group(self):
        '''
        Description:
            Hides this officer when joining a group, preventing it from being directly interacted with until the group is disbanded
        Input:
            None
        Output:
            None
        '''
        self.in_group = True
        self.selected = False
        self.hide_images()

    def leave_group(self, group):
        '''
        Description:
            Reveals this officer when its group is disbanded, allowing it to be directly interacted with. Also selects this officer, meaning that the officer will be selected rather than the worker when a group is disbanded
        Input:
            group group: group from which this officer is leaving
        Output:
            None
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.show_images()
        self.select()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #calibrate info display to officer's tile upon disbanding

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('officer_list', utility.remove_from_list(self.global_manager.get('officer_list'), self))
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.remove()

    def display_die(self, coordinates, result, min_success, min_crit_success, max_crit_fail):
        '''
        Description:
            Creates a die object at the inputted location and predetermined roll result to use for multi-step notification dice rolls. The color of the die's outline depends on the result
        Input:
            int tuple coordinates: Two values representing x and y pixel coordinates for the bottom left corner of the die
            int result: Predetermined result that the die will end on after rolling
            int min_success: Minimum roll required for a success
            int min_crit_success: Minimum roll required for a critical success
            int max_crit_fail: Maximum roll required for a critical failure
        Output:
            None
        '''
        result_outcome_dict = {'min_success': min_success, 'min_crit_success': min_crit_success, 'max_crit_fail': max_crit_fail}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)            

class evangelist(officer):
    '''
    Officer that can start religious campaigns and merge with church volunteers to form missionaries
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
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'veteran': boolean value - Required if from save, whether this officer is a veteran
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['officer_type'] = 'evangelist'
        super().__init__(from_save, input_dict, global_manager)
        self.current_roll_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6

    def start_religious_campaign(self): 
        '''
        Description:
            Used when the player clicks on the start religious campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the evangelist's
                movement points
        Input:
            None
        Output:
            None
        '''
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'evangelist': self,'type': 'start religious campaign'}
        self.global_manager.set('ongoing_religious_campaign', True)
        message = "Are you sure you want to start a religious campaign? /n /nIf successful, a religious campaign will convince church volunteers to join you, allowing the formation of groups of missionaries that can convert native "
        message += "villages. /n /n"
        risk_value = -1 * self.current_roll_modifier #modifier of -1 means risk value of 1
        if self.veteran: #reduce risk if veteran
            risk_value -= 1

        if risk_value < 0: #0/6 = no risk
            message = "RISK: LOW /n /n" + message  
        elif risk_value == 0: #1/6 death = moderate risk
            message = "RISK: MODERATE /n /n" + message #puts risk message at beginning
        elif risk_value == 1: #2/6 = high risk
            message = "RISK: HIGH /n /n" + message
        elif risk_value > 1: #3/6 or higher = extremely high risk
            message = "RISK: DEADLY /n /n" + message
            
        notification_tools.display_choice_notification(message, ['start religious campaign', 'stop religious campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def religious_campaign(self): #called when start religious campaign clicked in choice notification
        '''
        Description:
            Controls the religious campaign process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        text = ""
        text += "The evangelist campaigns for the support of church volunteers to join him in converting the African natives. /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'religious_campaign', self.global_manager)
        else:
            text += ("The veteran evangelist can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'religious_campaign', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            first_roll_list = dice_utility.roll_to_list(6, "Religous campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i >= self.current_min_crit_success:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            roll_list = dice_utility.roll_to_list(6, "Religious campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'religious_campaign', self.global_manager)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += "Inspired by the evangelist's message to save the heathens from their own ignorance, a group of church volunteers joins you. /n /n"
        else:
            text += "Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to gather any volunteers. /n /n"
        if roll_result <= self.current_max_crit_fail:
            text += "The evangelist is disturbed by the lack of faith of your country's people and decides to abandon your company. /n /n" #actual 'death' occurs when religious campaign completes

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += "With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_religious_campaign', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('religious_campaign_result', [self, roll_result])

    def complete_religious_campaign(self):
        '''
        Description:
            Used when the player finishes rolling for a religious campaign, shows the campaign's results and making any changes caused by the result. If successful, recruits church volunteers, promotes evangelist to a veteran on
                critical success. If not successful, the evangelist consumes its movement points and dies on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('religious_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            input_dict = {}
            input_dict['coordinates'] = (0, 0)
            input_dict['grids'] = [self.global_manager.get('europe_grid')]
            input_dict['image'] = 'mobs/church_volunteers/default.png'
            input_dict['name'] = 'Church volunteers'
            input_dict['modes'] = ['strategic', 'europe']
            input_dict['init_type'] = 'church_volunteers'
            self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
            #new_church_volunteers = workers.church_volunteers(False, input_dict, self.global_manager)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.select()
            for current_image in self.images: #move mob to front of each stack it is in - also used in button.same_tile_icon.on_click(), make this a function of all mobs to move to front of tile
                if not current_image.current_cell == 'none':
                    while not self == current_image.current_cell.contained_mobs[0]:
                        current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        elif roll_result <= self.current_max_crit_fail:
            self.die()
        self.global_manager.set('ongoing_religious_campaign', False)

class merchant(officer):
    def __init__(self, from_save, input_dict, global_manager):
        input_dict['officer_type'] = 'merchant'
        super().__init__(from_save, input_dict, global_manager)
        self.current_roll_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6

    def start_advertising_campaign(self, target_commodity): 
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'merchant': self, 'type': 'start advertising campaign', 'commodity': target_commodity}
        self.global_manager.set('ongoing_advertising_campaign', True)
        message = "Are you sure you want to start an advertising campaign for " + target_commodity + "? /n /n"
        risk_value = -1 * self.current_roll_modifier #modifier of -1 means risk value of 1
        if self.veteran: #reduce risk if veteran
            risk_value -= 1

        if risk_value < 0: #0/6 = no risk
            message = "RISK: LOW /n /n" + message  
        elif risk_value == 0: #1/6 death = moderate risk
            message = "RISK: MODERATE /n /n" + message #puts risk message at beginning
        elif risk_value == 1: #2/6 = high risk
            message = "RISK: HIGH /n /n" + message
        elif risk_value > 1: #3/6 or higher = extremely high risk
            message = "RISK: DEADLY /n /n" + message

        self.current_advertised_commodity = target_commodity
        self.current_unadvertised_commodity = random.choice(self.global_manager.get('commodity_types'))
        while (self.current_unadvertised_commodity == 'consumer goods') or (self.current_unadvertised_commodity == self.current_advertised_commodity) or (self.global_manager.get('commodity_prices')[self.current_unadvertised_commodity] == 1):
            self.current_unadvertised_commodity = random.choice(self.global_manager.get('commodity_types'))
        notification_tools.display_choice_notification(message, ['start advertising campaign', 'stop advertising campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def advertising_campaign(self): #called when start commodity icon clicked
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        text = ""
        text += "Merchant campaigns message. /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'advertising_campaign', self.global_manager)
        else:
            text += ("The veteran merchant can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'advertising_campaign', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            first_roll_list = dice_utility.roll_to_list(6, "Religous campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i >= self.current_min_crit_success:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            roll_list = dice_utility.roll_to_list(6, "Advertising campaign roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'advertising_campaign', self.global_manager)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += "Success message. The price of " + self.current_advertised_commodity + " increased by 1 to " + str(self.global_manager.get('commodity_prices')[self.current_advertised_commodity] + 1) + " and the price of "
            text += self.current_unadvertised_commodity + " decreased by 1 to " + str(self.global_manager.get('commodity_prices')[self.current_unadvertised_commodity] - 1) + ". /n /n"
        else:
            text += "Fail message. /n /n"
        if roll_result <= self.current_max_crit_fail:
            text += "Crit fail message. /n /n" #actual 'death' occurs when advertising campaign completes

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += "Crit success message. /n /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_advertising_campaign', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('advertising_campaign_result', [self, roll_result])

    def complete_advertising_campaign(self):
        roll_result = self.global_manager.get('advertising_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            #change prices
            market_tools.change_price(self.current_advertised_commodity, 1, self.global_manager)
            market_tools.change_price(self.current_unadvertised_commodity, -1, self.global_manager)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.select()
        elif roll_result <= self.current_max_crit_fail:
            self.die()
        self.global_manager.set('ongoing_advertising_campaign', False)
