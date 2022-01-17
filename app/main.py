import sys,os
from importlib import import_module

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware


import graphene
from graphene import Context
from starlette_graphene3 import GraphQLApp, make_graphiql_handler,make_playground_handler
from starlette_exporter import PrometheusMiddleware, handle_metrics

# from .models.redis import Redis
from app.graphql.query import Query
from app.routers import *

from app.utils.dataloader import get_dataloaders

app = FastAPI(title="Others API")

app.add_middleware(
    CORSMiddleware,
    # allow_origin_regex="https?://.*\.domain.com(:\d+)?",
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(PrometheusMiddleware,app_name="graphql", group_paths=True, prefix='fastapi',)

# GraphQL schema
schema = graphene.Schema(query=Query, auto_camelcase=False)
graphql_app = GraphQLApp(schema=schema, on_get=make_graphiql_handler(),context_value=get_dataloaders())
app.add_route("/graphql", graphql_app)


## Prometheus Metrics Route
app.add_route("/metrics", handle_metrics)



## dynamic add routers (files inside app/routers & `router` object)
from fastapi import APIRouter
routers = list(filter(lambda module: "app.routers" in module,sys.modules))
for router in routers:
    module = sys.modules[router]
    for path in module.__path__:
        for obj in os.scandir(path):
            if obj.is_file() and "__init__" not in obj.name:
                module = import_module("."+obj.name[:-3],package=router)                
                app_router = getattr(module, "router",None)
                if app_router and isinstance(app_router,APIRouter) :
                    app.include_router(app_router)

                    