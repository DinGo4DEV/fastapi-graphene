import uuid
import ujson

import pydantic
from pydantic.main import Extra

from graphene_pydantic import PydanticObjectType
import typing
from typing import ForwardRef, List,Dict,Optional

class TestDictModel(pydantic.BaseModel):
    dictOne:int
    dictTwo: int    

class TestDict(PydanticObjectType):
    class Meta:
        model = TestDictModel
        
    @classmethod
    def resolve_testDict(cls,parent,info,**kwargs):         
        
        if 'testDict' in parent:
            return TestDictModel(**parent['testDict'])
        else:
            return None
    
TestDict.resolve_placeholders()