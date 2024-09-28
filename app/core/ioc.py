from functools import lru_cache

from dishka import AsyncContainer, make_async_container

from .providers import DatabaseProvider, RepositoryProvider, ServiceProvider, ClientProvider



def init_container() -> AsyncContainer:
    return make_async_container(DatabaseProvider(), RepositoryProvider(), ServiceProvider(), ClientProvider())



@lru_cache(1)
def get_container() -> AsyncContainer:
    return init_container()