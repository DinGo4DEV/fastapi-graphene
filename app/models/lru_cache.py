from asyncio.log import logger
import functools
import logging
import pydantic
import ujson
import pickle

from collections import OrderedDict
from asyncio.futures import Future
from app.models.redis import my_redis

class LRUCache:
    cache = OrderedDict()
    redis = my_redis
    def __init__(self,model=None,maxsize:int=10,ttl:int=-1):
        """ Least Recently Used (LRU) cache Use for dataloader
        The cache will connect remote redis as remotecache

        Args:
            maxsize (int, optional): Capacity of the data in cache . Defaults to 10.
        """
        self.model = None
        self.maxsize = maxsize
        self.ttl = ttl
        pass
    
    
    def get(self,id):
        
        if id in self.cache:
            self.cache.move_to_end(id)
            return self.cache[id]

        try:
            data = self.redis.get(id)            
            if data is None:
                return None
            else:
                future = Future()
                future.set_result(pickle.loads(data))
                print(future)
                self.cache[id] = future
                return self.cache[id]
        except Exception as e:
            print(e)
            return None
    
    def __getitem__(self,key):
        return self.get(key)
        
    
    def __setitem__(self, name, value):
        self.cache[name] = value
        self.cache.move_to_end(name)
        future:Future = value        
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last = False)            
            
        ## If redis connection is On, Add callback funtion for Future when done
        if self.redis.active:
            future.add_done_callback(functools.partial(self._set_remote_cache,name))
            
    def update(self, *args, **kwargs):
        self.cache.update(**kwargs)
        return self
        

    def pop(self,key,default_value):
        if key in self.cache:
            try:
                return self.cache.pop(key)
            except:
                return default_value
        return default_value
                
    def clear(self):
        self.cache.clear()
        return self
        

    def _set_remote_cache(self,name,future:Future):
        result = future.result()
        if issubclass(type(result),pydantic.BaseModel):            
            self.redis.set(name,pickle.dumps(result),ex = self.ttl if self.ttl and self.ttl > 0 else None)
            # self.redis.set(name,result.json(),ex = self.ttl if self.ttl and self.ttl > 0 else None)
        else:
            self.redis.set(name,result,ex=30)

    def __len__(self):
        return len(self.cache)