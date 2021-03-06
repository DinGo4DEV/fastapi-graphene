from inspect import isclass, ismodule,getmembers
import pydantic
from aiodataloader import DataLoader
from graphene_pydantic import PydanticObjectType

from app.models.dataloader import MyDataLoader
from app.graphql import schema





DATALOADERS = {}
BATCH_LOAD_FN_NAME = "batch_load_fn"
DATALOADER_CLASS = "DataLoader"

def get_dataloaders():
    """ Auto Create Dataloader when startup Graphql
    Two way to auto generate DataLoader:
    
        Define a class `DataLoader` in schema `PydanticObjectType` or `ObjectType` with following optional attrs:
        
            model = `DataLoader` | `MyDataLoader`
            
            cache_map (cache): `LRUCache(maxsize:int, ttl:int)` | `{}`
            
            async def `batch_load_fn(cls,keys)`
        
        Define a `async def batch_load_fn` class method in schema `PydanticObjectType` or `ObjectType`,
            This will auto use `MyDataLoader` and `LRUCache` with 1 min TTL and 10 capacity cache
    """
    CLASSES = _reduce_classes(map(_get_schema_classes,_get_schema_modules().values()))
    for name,cls in CLASSES.items():
        # print(cls.__dict__)
        batch_load_fn = getattr(cls,BATCH_LOAD_FN_NAME,None)
        if batch_load_fn:
            if name not in DATALOADERS:
                DATALOADERS[name] = MyDataLoader(batch_load_fn)
                continue
        dataloader = getattr(cls,DATALOADER_CLASS,None)              
        if dataloader:
            batch_load_fn = getattr(dataloader,BATCH_LOAD_FN_NAME,None)
            if batch_load_fn is None:
                raise AttributeError(f"No {BATCH_LOAD_FN_NAME} is define on the {dataloader}")            
            
            ## if model and cachemap, will use Default DataLoader from `aiodataloader`
            if getattr(dataloader,"model",None) is None:
                dataloader.model = DataLoader
            if getattr(dataloader,"cachemap",None) is None is None:
                dataloader.cachemap = {}
                
            if name not in DATALOADERS:
                DATALOADERS[name] = dataloader.model(batch_load_fn,cache_map=dataloader.cachemap)
    return DATALOADERS

## Recursive Load the moudles in schema
def _get_moudles(module):
    schema_modules = {}
    for name,value in getmembers(module):        
        if ismodule(value):
            ## Checking the moudle is namespace
            if hasattr(value, "__path__") and (getattr(value, '__file__', None) is None or "__init__" in getattr(value, '__file__', None)):
                schema_modules.update(_get_moudles(value))
            else: schema_modules[name] = value        
    return schema_modules


def _get_schema_modules():
    schema_modules = {}
    schema_modules = _get_moudles(schema)
    return schema_modules

def _get_schema_classes(module):
    return getmembers(module,_predict_class)
    
def _reduce_classes(classes):
    """[summary]

    Args:
        classes ([type]): [description]

    Returns:
        [type]: [description]
    """
    out = dict()
    for cls in classes:
        for name,cls in cls:
            out[name] = cls
    return out

def _predict_class(cls):
    """
    Predict the class == `PydanticObjectTpye` or `pydantic.BaseModel`
    
    Args:
        cls (Any): Any attrs on the moudule pass on `getmembers`
    Returns:
        [bool]: `True` or `False`
    """
    return isclass(cls) and ((issubclass(cls,PydanticObjectType) and not cls==PydanticObjectType)
                               or issubclass(cls,pydantic.BaseModel))