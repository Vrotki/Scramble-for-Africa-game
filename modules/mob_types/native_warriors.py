#Contains functionality for native warriors units

import random
from .npmobs import npmob
from .. import utility

class native_warriors(npmob):
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)
        self.hostile = True
        self.saves_normally = False #saves as part of village
        self.origin_village = input_dict['origin_village']
        self.origin_village.attached_warriors.append(self)
        self.npmob_type = 'native_warriors'

    def remove(self):
        super().remove()
        self.origin_village.attached_warriors = utility.remove_from_list(self.origin_village.attached_warriors, self)

    def check_despawn(self):
        if random.randrange(1, 7) == 1:
            self.remove()
            self.origin_village.change_population(1)
