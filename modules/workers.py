#Contains functionality for worker units
import random

from .mobs import mob
from . import actor_utility
from . import utility
from . import market_tools
from . import text_tools

class worker(mob):
    '''
    Mob that is required for resource buildings to produce commodities, officers to form group, and vehicles to function
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
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'worker_type': string value - Type of worker this is, like 'European'. Each type of worker has a separate upkeep, labor pool, and abilities
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        global_manager.get('worker_list').append(self)
        self.is_worker = True
        self.is_church_volunteers = False
        self.worker_type = input_dict['worker_type']
        
        if self.worker_type == 'European': #European church volunteers don't count for this because they have no upkeep
            self.global_manager.set('num_european_workers', self.global_manager.get('num_european_workers') + 1)
            if not from_save:
                market_tools.attempt_worker_upkeep_change('increase', self.worker_type, self.global_manager)
            
        elif self.worker_type == 'African':
            self.global_manager.set('num_african_workers', self.global_manager.get('num_african_workers') + 1)
            if not from_save:
                market_tools.attempt_worker_upkeep_change('increase', self.worker_type, self.global_manager)
                
        self.set_controlling_minister_type(self.global_manager.get('type_minister_dict')['production'])
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_worker changing

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
                'end_turn_destination': string or int tuple value- 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - How many movement points this actor currently has
                'image': string value - File path to the image used by this object
                'worker_type': string value - Type of worker this is, like 'European'. Each type of worker has a separate upkeep, labor pool, and abilities
        '''
        save_dict = super().to_save_dict()
        save_dict['worker_type'] = self.worker_type
        return(save_dict)

    def fire(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Additionally has a chance to decrease the upkeep of other workers of this worker's type by increasing the size of
                the labor pool
        Input:
            None
        Output:
            None
        '''
        super().fire()
        if self.worker_type in ['African', 'European']: #not religious volunteers
            market_tools.attempt_worker_upkeep_change('decrease', self.worker_type, self.global_manager)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this worker's tooltip can be shown. Along with the superclass' requirements, worker tooltips can not be shown when attached to another actor, such as when part of a group
        Input:
            None
        Output:
            None
        '''
        if not (self.in_group or self.in_vehicle):
            return(super().can_show_tooltip())
        else:
            return(False)

    def crew_vehicle(self, vehicle): #to do: make vehicle go to front of info display
        '''
        Description:
            Orders this worker to crew the inputted vehicle, attaching this worker to the vehicle and allowing the vehicle to function
        Input:
            vehicle vehicle: vehicle to which this worker is attached
        Output:
            None
        '''
        self.in_vehicle = True
        self.selected = False
        self.hide_images()
        vehicle.crew = self
        vehicle.has_crew = True
        vehicle.set_image('crewed')
        moved_mob = vehicle
        for current_image in moved_mob.images: #moves vehicle to front
            if not current_image.current_cell == 'none':
                while not moved_mob == current_image.current_cell.contained_mobs[0]:
                    current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        if not vehicle.initializing: #don't select vehicle if loading in at start of game
            vehicle.select()

    def uncrew_vehicle(self, vehicle):
        '''
        Description:
            Orders this worker to stop crewing the inputted vehicle, making this worker independent from the vehicle and preventing the vehicle from functioning
        Input:
            vehicle vehicle: vehicle to which this worker is no longer attached
        Output:
            None
        '''
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        self.show_images()
        vehicle.crew = 'none'
        vehicle.has_crew = False
        vehicle.set_image('uncrewed')
        vehicle.end_turn_destination = 'none'
        vehicle.hide_images()
        vehicle.show_images() #bring vehicle to front of tile
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)

    def join_group(self):
        '''
        Description:
            Hides this worker when joining a group, preventing it from being directly interacted with until the group is disbanded
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
            Reveals this worker when its group is disbanded, allowing it to be directly interacted with. Does not select this worker, meaning that the officer will be selected rather than the worker when a group is disbanded
        Input:
            group group: group from which this worker is leaving
        Output:
            None
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.show_images()

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
        self.global_manager.set('worker_list', utility.remove_from_list(self.global_manager.get('worker_list'), self))
        if self.worker_type == 'European': #European church volunteers don't count for this because they have no upkeep
            self.global_manager.set('num_european_workers', self.global_manager.get('num_european_workers') - 1)
        elif self.worker_type == 'African':
            self.global_manager.set('num_african_workers', self.global_manager.get('num_african_workers') - 1)

class slave_worker(worker):
    '''
    Worker that is captured or bought from slave traders, reduces public opinion, and has a low, unvarying upkeep and a varying recruitment cost
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
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'purchased': boolean value - Value set to true if the slaves were bought or false if they were captured, determining effects on public opinion and slave recruitment costs
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['worker_type'] = 'slave'
        super().__init__(from_save, input_dict, global_manager)
        if not from_save:
            if input_dict['purchased']: #as opposed to captured
                market_tools.attempt_slave_recruitment_cost_change('increase', self.global_manager)
                public_opinion_penalty = 5 + random.randrange(-3, 4) #2-8
                current_public_opinion = self.global_manager.get('public_opinion_tracker').get()
                self.global_manager.get('public_opinion_tracker').change(-1 * public_opinion_penalty)
                resulting_public_opinion = self.global_manager.get('public_opinion_tracker').get()
                if not resulting_public_opinion == current_public_opinion:
                    text_tools.print_to_screen("Participating in the slave trade has decreased your public opinion from " + str(current_public_opinion) + " to " + str(resulting_public_opinion) + ".", self.global_manager)
        self.global_manager.set('num_slave_workers', self.global_manager.get('num_slave_workers') + 1)
        self.set_controlling_minister_type(self.global_manager.get('type_minister_dict')['production'])
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_worker changing

    def fire(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Firing a slave worker unit also frees them, increasing public opinion and adding them to the labor pool
        Input:
            None
        Output:
            None
        '''
        super().fire()
        market_tools.attempt_worker_upkeep_change('decrease', 'African', self.global_manager)
        public_opinion_bonus = 4 + random.randrange(-3, 4) #1-7, less bonus than penalty for buying slaves on average
        current_public_opinion = self.global_manager.get('public_opinion_tracker').get()
        self.global_manager.get('public_opinion_tracker').change(public_opinion_bonus)
        resulting_public_opinion = self.global_manager.get('public_opinion_tracker').get()
        if not resulting_public_opinion == current_public_opinion:
            text_tools.print_to_screen("Freeing slaves has increased your public opinion from " + str(current_public_opinion) + " to " + str(resulting_public_opinion) + ".", self.global_manager)

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
        self.global_manager.set('num_slave_workers', self.global_manager.get('num_slave_workers') - 1)
        self.global_manager.set('worker_list', utility.remove_from_list(self.global_manager.get('worker_list'), self))

class church_volunteers(worker):
    '''
    Worker with no cost that can join with a head missionary to form missionaries, created through religious campaigns
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
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.set_controlling_minister_type(self.global_manager.get('type_minister_dict')['religion'])
        self.is_church_volunteers = True
