from aiodataloader import DataLoader
from app.models.lru_cache import LRUCache
    

class MyDataLoader(DataLoader):
    PREFIX_CACHE_KEY = "fastapi:graphql"    
    def __init__(self, batch_load_fn=None, batch=None, max_batch_size=None, cache=None, get_cache_key=None, cache_map=None, loop=None):
        """
        DataLoader for graphql, **the dataloader Only work when using aysncio framwork**

        Args:
            batch_load_fn (func, optional): func for the load. Defaults to None.
            batch (bool, optional): Bool to delacre whether should use batch. Defaults to None.
            max_batch_size (int, optional): Max size for one batch_load_many. Defaults to None.
            cache (bool, optional): Bool to delcare whether should use cache. Defaults to None.
            get_cache_key (str, optional): key storing the result to cache. Defaults to None.
            cache_map ([dict,LRUCache], optional): cache for the `Future`. Defaults to None.
            loop (evnetloop, optional): the event loop which is running the application. Defaults to None.
        """
        
        cls_name = batch_load_fn.__qualname__.rsplit('.', 1)[0]
        get_cache_key = lambda x: f"{self.PREFIX_CACHE_KEY}:{cls_name}:{x}"
        cache_map  = LRUCache()
        super().__init__(batch_load_fn=batch_load_fn, batch=batch, max_batch_size=max_batch_size, cache=cache, get_cache_key=get_cache_key, cache_map=cache_map, loop=loop)