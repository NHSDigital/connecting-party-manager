from pydantic import UUID4, BaseModel


class ProductId(BaseModel):
    id: UUID4


class ReadProductTeamEvent(BaseModel):
    pathParameters: ProductId
