import random
from uuid import UUID


def consistent_uuid(seed: int | str) -> str:
    random.seed(seed)
    return str(UUID(int=random.getrandbits(128)))
