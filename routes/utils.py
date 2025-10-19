from pydantic.v1.fields import T
from pydantic.v1.generics import GenericModel
from typing import List, Generic


class PaginatedResponse(GenericModel, Generic[T]):
    total: int
    skip: int
    limit: int
    data: List[T]