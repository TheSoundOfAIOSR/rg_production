from enum import Enum

class StateEnum(Enum):
    Exit = -1
    Loading = 0
    Update = 1
    Playing_Idle = 2
    Recording = 3
    Inferring_Pipeline = 4
    New_Text = 5
    New_Descriptor_Generation = 6
    New_Sound_Generation = 7
    Preprocessing = 8