import os

from pynamodb.attributes import DiscriminatorAttribute, UnicodeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model


class GlobalSecondaryIndexOne(GlobalSecondaryIndex):
    pk_1 = UnicodeAttribute(hash_key=True)
    sk_1 = UnicodeAttribute(range_key=True)

    class Meta:
        index_name = "gsi_1"
        projection = AllProjection()


class GlobalSecondaryIndexTwo(GlobalSecondaryIndex):
    pk_2 = UnicodeAttribute(hash_key=True)
    sk_2 = UnicodeAttribute(range_key=True)

    class Meta:
        index_name = "gsi_2"
        projection = AllProjection()


class BaseModel(Model):
    class Meta:
        table_name = os.environ.get("DYNAMODB_TABLE")
        region = "eu-west-2"
        abstract = True

    cls = DiscriminatorAttribute()
    pk = UnicodeAttribute(hash_key=True)
    sk = UnicodeAttribute(range_key=True)

    pk_1 = UnicodeAttribute()
    sk_1 = UnicodeAttribute()
    gsi_1 = GlobalSecondaryIndexOne()

    pk_2 = UnicodeAttribute()
    sk_2 = UnicodeAttribute()
    gsi_2 = GlobalSecondaryIndexTwo()

    def __init__(self, **kwargs):
        if "id" in kwargs:
            pk = f"{self.__class__.__name__}#{kwargs['id']}"
            super().__init__(pk=pk, sk=pk, **kwargs)
        else:
            super().__init__(**kwargs)


class ProductTeam(BaseModel, discriminator="ProductTeam"):
    id = UnicodeAttribute()
    name = UnicodeAttribute()
    organisation = UnicodeAttribute()
    owner = UnicodeAttribute()
