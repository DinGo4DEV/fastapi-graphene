import ujson
from graphene.types import Scalar
class JSON(Scalar):
    """
    Allows use of a JSON  for input / output from the GraphQL schema.

    """
    
    # @staticmethod
    # def parse_literal(ast):
    #     print(ast)
    #     if isinstance(ast, (ast.StringValueNode)):
    #         return ast.value
        
    serialize = lambda v: v
    parse_value = lambda v: ujson.loads(v)
