#Contains functionality for creating new instances of mobs, buildings, and ministers

from . import actors
from . import mobs
from . import workers
from . import officers
from . import groups
from . import vehicles
from . import buildings
from . import ministers

class actor_creation_manager_template(): #can get instance from anywhere and create actors with it without importing respective actor module
    '''
    Object that creates new mobs and buildings based on inputted values
    '''
    def __init__(self):
        '''
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        '''
        nothing = 0
        
    def create(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes a mob or building based on inputted values
        Input:
            boolean from_save: True if the object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize the object, with contents varying based on the type of object
                'init_type': string value - Always required, determines type of object created
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            actor: Returns the mob or building that was created
        '''
        init_type = input_dict['init_type']

        #mobs
        if init_type == 'mob':
            new_actor = mobs.mob(from_save, input_dict, global_manager)
        elif init_type == 'worker':
            new_actor = workers.worker(from_save, input_dict, global_manager)
        elif init_type == 'church_volunteers':
            new_actor = workers.church_volunteers(from_save, input_dict, global_manager)
        elif init_type == 'train':
            new_actor = vehicles.train(from_save, input_dict, global_manager)
        elif init_type == 'ship':
            new_actor = vehicles.ship(from_save, input_dict, global_manager)
        elif init_type in global_manager.get('officer_types'):
            if init_type == 'evangelist':
                new_actor = officers.evangelist(from_save, input_dict, global_manager)
            elif init_type == 'merchant':
                new_actor = officers.merchant(from_save, input_dict, global_manager)
            else:
                new_actor = officers.officer(from_save, input_dict, global_manager)
        elif init_type == 'porters':
            new_actor = groups.porters(from_save, input_dict, global_manager)
        elif init_type == 'work_crew':
            new_actor = groups.work_crew(from_save, input_dict, global_manager)
        elif init_type == 'construction_gang':
            new_actor = groups.construction_gang(from_save, input_dict, global_manager)
        elif init_type == 'caravan':
            new_actor = groups.caravan(from_save, input_dict, global_manager)
        elif init_type == 'missionaries':
            new_actor = groups.missionaries(from_save, input_dict, global_manager)
        elif init_type == 'expedition':
            new_actor = groups.expedition(from_save, input_dict, global_manager)

        #buildings
        elif init_type == 'infrastructure':
            new_actor = buildings.infrastructure_building(from_save, input_dict, global_manager)
        elif init_type == 'trading_post':
            new_actor = buildings.trading_post(from_save, input_dict, global_manager)
        elif init_type == 'mission':
            new_actor = buildings.mission(from_save, input_dict, global_manager)
        elif init_type == 'train_station':
            new_actor = buildings.train_station(from_save, input_dict, global_manager)
        elif init_type == 'port':
            new_actor = buildings.port(from_save, input_dict, global_manager)
        elif init_type == 'resource':
            new_actor = buildings.resource_building(from_save, input_dict, global_manager)
        return(new_actor)

    def create_group(self, worker, officer, global_manager): #use when merging groups. At beginning of game, instead of using this, create a group which creates its worker and officer and merges them
        '''
        Description:
            Creates a group out of the inputted worker and officer. The type of group formed depends on the officer's type. Upon joining a group, the component officer and worker will not be able to be seen or interacted with
                independently until the group is disbanded
        Input:
            worker worker: worker to create a group out of
            officer officer: officer to create a group out of
        Output:
            None
        '''
        input_dict = {}
        input_dict['coordinates'] = (officer.x, officer.y)
        input_dict['grids'] = officer.grids
        input_dict['worker'] = worker
        input_dict['officer'] = officer
        #input_dict['modes'] = ['strategic', 'europe']
        input_dict['modes'] = input_dict['grids'][0].modes #if created in Africa grid, should be ['strategic']. If created in Europe, should be ['strategic', 'europe']
        input_dict['init_type'] = global_manager.get('officer_group_type_dict')[officer.officer_type]
        input_dict['image'] = 'mobs/' + officer.officer_type + '/' + input_dict['init_type'] + '.png' #mobs/merchant/caravan.png
        name = ''
        for character in input_dict['init_type']:
            if not character == '_':
                name += character
            else:
                name += ' '
        input_dict['name'] = name
        return(self.create(False, input_dict, global_manager))

    def create_placeholder_ministers(self, global_manager):
        '''
        Description:
            Creates 10 non-appointed ministers at the start of the game
        Input:
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        for i in range(0, 10):
            new_minister = ministers.minister(False, {}, global_manager)

    def load_minister(self, input_dict, global_manager):
        '''
        Description:
            Initializes a minister based on the inputted values
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'name': string value - The minister's name
                'current_position': string value - Office that the minister is currently occupying, or 'none' if no office occupied
                'general_skill': int value - Value from 1 to 3 that changes what is added to or subtracted from dice rolls
                'specific_skills': dictionary value - String keys corresponding to int values to record skill values for each minister office
                'corruption': int value - Measure of how corrupt a minister is, with 6 having a 1/2 chance to steal, 5 having 1/3 chance, etc.
                'image_id': string value - File path to the image used by the minister
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        new_minister = ministers.minister(True, input_dict, global_manager)