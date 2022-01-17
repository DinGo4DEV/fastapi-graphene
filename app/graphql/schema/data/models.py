import uuid
import ujson

import pydantic
from pydantic.main import Extra

from graphene_pydantic import PydanticObjectType

import typing
from typing import ForwardRef, List,Dict,Optional

from app.graphql.schema.data.test_dict import TestDictModel

class DataModel(pydantic.BaseModel):
    id: int
    testInt: int
    # testList: Optional[List[typing.Any]]
    testDict: Optional[TestDictModel]
    

class Data(PydanticObjectType):
    # inlineVideos: typing.Optional[typing.List[InlineVideoModel]]
    class Meta:
        model = DataModel
        # only_fields=[AritcalModel.fields]
        
    @classmethod
    async def batch_load_fn(cls,keys):
        print(f"{cls.__name__} is loaded with key={keys}")
        out = {}
        for key in keys:
            with open(f"res/data{key}.json","r",encoding="utf-8") as f:
                data= ujson.load(f)
            out.update({key: DataModel(**data)})
        # return Promise.resolve([out.get(id) for id in keys])
        return [out.get(id) for id in keys]
        
    @classmethod
    def resolve_data(cls,parent,info,**kwargs):
        if kwargs['id'] is None:
            return info.context[cls.__name__].load(1)
        return info.context[cls.__name__].load(kwargs['id'])
    
Data.resolve_placeholders()