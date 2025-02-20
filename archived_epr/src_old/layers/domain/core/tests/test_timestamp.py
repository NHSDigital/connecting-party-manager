from datetime import date, datetime

from domain.core.timestamp import now
from pydantic import BaseModel


def test_now():
    class MyModel(BaseModel):
        my_date: datetime

    my_model = MyModel(my_date=now())
    assert my_model.my_date.date() == date.today()
