import pytest
import logging
from collections import namedtuple

from asyncio.futures import Future

from app.models.lru_cache import LRUCache



Case = namedtuple("Case", ["cache_len", "init","expect_len"])

logger = logging.getLogger()


@pytest.mark.parametrize(
    "case",
    [
        Case(10, [], 0),
        Case(10, [("test:one", 1)], 1),
        Case(10, [("test:one", 1), ("test:two", 2)], 2),
        Case(2,  [("test:one", 1), ("test:two", 2)], 2),
        Case(1,  [("test:one", 1), ("test:two", 2)], 1),
    ],
)

@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["init"])
async def test_cache_init(event_loop,case, method):
    """Check that the # of elements is right, given # given and cache_len."""
    if method == "init":
        cache = LRUCache(maxsize=case.cache_len)
        for (key, val) in case.init:
            future = Future(loop=event_loop)            
            cache[key] = future
            future.set_result(val)
            assert future.done()            
    else:
        assert False
    # length is max(#entries, cache_len)
    assert len(cache) == case.expect_len



# @pytest.mark.asyncio
# @pytest.mark.parametrize("method", ["init"])
# async def test_get_remote_redis(event_loop,case, method):
#     """Check that the # of elements is right, given # given and cache_len."""
#     if method == "init":
#         cache = LRUCache(maxsize=case.cache_len)
#         for (key, val) in case.init:
#             future = Future(loop=event_loop)            
#             cache[key] = future
#             future.set_result(val)
#             assert future.done()            
#     else:
#         assert False
#     # length is max(#entries, cache_len)
#     assert len(cache) == case.expect_len