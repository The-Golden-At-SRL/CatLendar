from enum import Enum
from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field, field_validator

class Languages(Enum):
    English = "English"
    Italian = "Italian"
    
class MySettings(BaseModel):
    language: Languages = Languages.English
    
@plugin
def settings_model():
    return MySettings