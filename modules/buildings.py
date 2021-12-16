#Contains functionality for buildings

import pygame
from .actors import actor
from .buttons import button
from . import utility
from . import images
from . import actor_utility
from . import text_tools

class building(actor):
    '''
    Actor that exists in cells of multiple grids in front of tiles and behind mobs that can not be clicked
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
                'name': string value - Required if from save, this building's name
                'building_type': string value - Type of building, like 'port'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_type = 'building'
        self.building_type = input_dict['building_type']
        super().__init__(from_save, input_dict, global_manager)
        self.image_dict = {'default': input_dict['image']}
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.building_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default',
                self.global_manager)) #self, actor, width, height, grid, image_description, global_manager
        self.global_manager.get('building_list').append(self)
        self.set_name(input_dict['name'])
        self.work_crew_capacity = 0 #default
        self.contained_work_crews = []
        if from_save:
            for current_work_crew in input_dict['contained_work_crews']:
                self.global_manager.get('actor_creation_manager').create(True, current_work_crew, self.global_manager).work_building(self)
        for current_image in self.images:
            current_image.current_cell.contained_buildings[self.building_type] = self
            current_image.current_cell.tile.update_resource_icon()
        self.is_port = False #used to determine if port is in a tile to move there

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
                'modes': string list value - Game modes during which this building's images can appear
                'grid_type': string value - String matching the global manager key of this building's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': string/string dictionary value - Version of this building's inventory dictionary only containing commodity types with 1+ units held
                'building_type': string value - Type of building, like 'port'
                'image': string value - File path to the image used by this object
                'contained_work_crews': dictionary list value - list of dictionaries of saved information necessary to recreate each work crew working in this building
        '''
        save_dict = super().to_save_dict()
        save_dict['building_type'] = self.building_type
        save_dict['contained_work_crews'] = [] #list of dictionaries for each work crew, on load a building creates all of its work crews and attaches them
        save_dict['image'] = self.image_dict['default']
        for current_work_crew in self.contained_work_crews:
            save_dict['contained_work_crews'].append(current_work_crew.to_save_dict())
        return(save_dict)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also removes this building from the tiles it occupies
        Input:
            None
        Output:
            None
        '''
        tiles = []
        for current_image in self.images:
            if not current_image.current_cell == 'none':
                tiles.append(current_image.current_cell.tile)
            current_image.current_cell.contained_buildings[self.building_type] = 'none'
            current_image.remove_from_cell()
            current_image.remove()
        super().remove()
        self.global_manager.set('building_list', utility.remove_from_list(self.global_manager.get('building_list'), self))
        for current_tile in tiles:
            current_tile.update_resource_icon()
        if self.global_manager.get('displayed_tile') in tiles: #if currently displayed, update tile to show building removal
            self.global_manager.get('minimap_grid').calibrate(self.x, self.y)

    def update_tooltip(self): #should be shown below mob tooltips
        '''
        Description:
            Sets this image's tooltip to what it should be whenever the player looks at the tooltip. For buildings, sets tooltip to a description of the building
        Input:
            None
        Output:
            None
        '''
        tooltip_text = [self.name.capitalize()]
        if self.building_type == 'resource':
            tooltip_text.append("Work crew capacity: " + str(len(self.contained_work_crews)) + '/' + str(self.work_crew_capacity))
            if len(self.contained_work_crews) == 0:
                tooltip_text.append("Work crews: none")
            else:
                tooltip_text.append("Work crews: ")
            for current_work_crew in self.contained_work_crews:
                tooltip_text.append("    " + current_work_crew.name)
            tooltip_text.append("Produces 1 unit of " + self.resource_type + " per attached work crew per turn")
        elif self.building_type == 'port':
            tooltip_text.append("Allows ships to enter this tile")
        elif self.building_type == 'infrastructure':
            tooltip_text.append("Halves movement cost for units going to another tile with a road or railroad")
            if self.is_railroad:
                tooltip_text.append("Allows trains to move from this tile to other tiles that have railroads")
            else:
                tooltip_text.append("Can be upgraded to a railroad to allow trains to move through this tile")
        elif self.building_type == 'train_station':
            tooltip_text.append("Allows construction gangs to build trains on this tile")
            tooltip_text.append("Allows trains to drop off or pick up cargo or passengers in this tile")
        self.set_tooltip(tooltip_text)

    def touching_mouse(self):
        '''
        Description:
            Returns whether any of this building's images is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if any of this building's images is colliding with the mouse, otherwise returns False
        '''
        for current_image in self.images:
            if current_image.change_with_other_images: #don't show tooltips for road connection images, only the base road building images
                if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                    if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                        return(True)
        return(False)

class infrastructure_building(building):
    '''
    Building that eases movement between tiles and is a road or railroad. Has images that show connections with other tiles that have roads or railroads
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
                'name': string value - Required if from save, this building's name
                'infrastructure_type': string value - Type of infrastructure, like 'road', or 'railroad'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.infrastructure_type = input_dict['infrastructure_type']
        if self.infrastructure_type == 'railroad':
            self.is_road = False
            self.is_railroad = True
        elif self.infrastructure_type == 'road':
            self.is_railroad = False
            self.is_road = True
        input_dict['building_type'] = 'infrastructure'
        super().__init__(from_save, input_dict, global_manager)
        self.image_dict['left_road'] = 'buildings/infrastructure/left_road.png'
        self.image_dict['right_road'] = 'buildings/infrastructure/right_road.png'
        self.image_dict['down_road'] = 'buildings/infrastructure/down_road.png'
        self.image_dict['up_road'] = 'buildings/infrastructure/up_road.png'
        self.image_dict['left_railroad'] = 'buildings/infrastructure/left_railroad.png'
        self.image_dict['right_railroad'] = 'buildings/infrastructure/right_railroad.png'
        self.image_dict['down_railroad'] = 'buildings/infrastructure/down_railroad.png'
        self.image_dict['up_railroad'] = 'buildings/infrastructure/up_railroad.png'
        self.image_dict['empty'] = 'misc/empty.png'
        self.infrastructure_connection_images = {}
        for current_grid in self.grids:
            up_image = images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'up', self.global_manager)
            down_image = images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'down', self.global_manager)
            right_image = images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'right', self.global_manager)
            left_image = images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'left', self.global_manager)
            #actor, width, height, grid, image_description, direction, global_manager
            self.images.append(up_image)
            self.images.append(down_image)
            self.images.append(right_image)
            self.images.append(left_image)
            self.infrastructure_connection_images['up'] = up_image
            self.infrastructure_connection_images['down'] = down_image
            self.infrastructure_connection_images['right'] = right_image
            self.infrastructure_connection_images['left'] = left_image
        actor_utility.update_roads(self.global_manager)

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
                'modes': string list value - Game modes during which this building's images can appear
                'grid_type': string value - String matching the global manager key of this building's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': string/string dictionary value - Version of this building's inventory dictionary only containing commodity types with 1+ units held
                'building_type': string value - Type of building, like 'infrastructure'
                'image': string value - File path to the image used by this object
                'contained_work_crews': dictionary list value - list of dictionaries of saved information necessary to recreate each work crew working in this building
                'infrastructure_type': string value - Type of infrastructure, like 'road' or 'railroad'
        '''
        save_dict = super().to_save_dict()
        save_dict['infrastructure_type'] = self.infrastructure_type
        return(save_dict)

class trading_post(building):
    '''
    Building in a village that allows trade with the village
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'trading_post'
        super().__init__(from_save, input_dict, global_manager)

class mission(building):
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'mission'
        super().__init__(from_save, input_dict, global_manager)

class train_station(building):
    '''
    Building along a railroad that allows the construction of train, allows trains to pick up and drop off cargo/passengers, and increases the tile's inventory capacity
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'train_station'
        super().__init__(from_save, input_dict, global_manager)
        for current_image in self.images:
            current_image.current_cell.tile.inventory_capacity += 9

class port(building):
    '''
    Building adjacent to water that allows ships to enter the tile, allows ships to travel to this tile if it is along the ocean, and increases the tile's inventory capacity
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
                'name': string value - Required if from save, this building's name
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['building_type'] = 'port'
        super().__init__(from_save, input_dict, global_manager)
        self.is_port = True #used to determine if port is in a tile to move there
        for current_image in self.images:
            current_image.current_cell.tile.inventory_capacity += 9

class resource_building(building):
    '''
    Building in a resource tile that allows work crews to attach to this building to produce commodities over time
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
                'name': string value - Required if from save, this building's name
                'resource_type': string value - Type of resource produced by this building, like 'exotic wood'
                'modes': string list value - Game modes during which this building's images can appear
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.resource_type = input_dict['resource_type']
        input_dict['building_type'] = 'resource'
        self.scale = 1
        self.efficiency = 1
        self.num_upgrades = 0
        super().__init__(from_save, input_dict, global_manager)
        global_manager.get('resource_building_list').append(self)
        for current_image in self.images:
            current_image.current_cell.tile.inventory_capacity += 9
        if from_save:
            while self.scale < input_dict['scale']:
                self.upgrade('scale')
            while self.efficiency < input_dict['efficiency']:
                self.upgrade('efficiency')

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
                'modes': string list value - Game modes during which this building's images can appear
                'grid_type': string value - String matching the global manager key of this building's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': string/string dictionary value - Version of this building's inventory dictionary only containing commodity types with 1+ units held
                'building_type': string value - Type of building, like 'infrastructure'
                'image': string value - File path to the image used by this object
                'contained_work_crews': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each work crew working in this building
                'resource_type': string value - Type of resource produced by this building, like 'exotic wood'
        '''
        save_dict = super().to_save_dict()
        save_dict['resource_type'] = self.resource_type
        save_dict['scale'] = self.scale
        save_dict['efficiency'] = self.efficiency
        return(save_dict)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, and removes it from the tiles it occupies
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('resource_building_list', utility.remove_from_list(self.global_manager.get('resource_building_list'), self))
        super().remove()

    def can_upgrade(self, upgrade_type):
        if upgrade_type == 'scale': #quantitative
            if self.scale < 6:
                return(True)
        elif upgrade_type == 'efficiency':
            if self.efficiency < 6:
                return(True)
        return(False)

    def upgrade(self, upgrade_type):
        if upgrade_type == 'scale':
            self.scale += 1
        elif upgrade_type == 'efficiency':
            self.efficiency += 1
        self.num_upgrades += 1

    def get_upgrade_cost(self):
        return(2 * (self.num_upgrades + 1)) #2 for 1st upgrade, 4 for 2nd, 6 for 3rd, etc.
    
    def produce(self):
        for current_work_crew in self.contained_work_crews:
            current_work_crew.attempt_production(self)
