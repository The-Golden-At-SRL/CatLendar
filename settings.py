from enum import Enum
from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, Field, field_validator

class Languages(Enum):
    English = "English"
    Italian = "Italian"
    
class GenerateContext(Enum):
    Yes = True
    No = False
    
class MySettings(BaseModel):
    language: Languages = Languages.English
    generate_context: GenerateContext = GenerateContext.Yes
    
@plugin
def settings_model():
    return MySettings