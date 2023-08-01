#Contains functionality for dummies, which replicate other objects or act as models of hypothetical objects with fake attribute values and tooltips 

from . import mobs

class dummy(mobs.mob):
    def __init__(self, input_dict, global_manager):
        '''
        input dict always includes dummy_type, which is generally equal to the init type of the unit being replicated?
        '''
        for key in input_dict:
            setattr(self, key, input_dict[key])
        self.global_manager = global_manager

    def set_tooltip(self, tooltip_text):
        self.tooltip_text = tooltip_text

    def get_image_id_list(self):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        return(self.image_id_list)
