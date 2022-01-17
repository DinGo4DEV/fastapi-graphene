import ujson
import graphene
from graphene import ObjectType,Field,List,ID,String
from graphene_pydantic import PydanticObjectType

from app.graphql.scalars.json import JSON
from app.graphql.schema.data import models


class Query(ObjectType):
    raw_json = Field(JSON) # DEMO: Custom Scalar JSON 
    
    data = Field(models.Data,id=ID(),resolver=models.Data.resolve_data)

    def resolve_raw_json(self,info,**kwargs):         
        with open("res/data1.json","r",encoding="utf-8") as f:
            data= ujson.load(f)
        return data

    
