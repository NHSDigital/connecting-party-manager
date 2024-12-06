import argparse
import json
import os

from domain.core.cpm_system_id import ProductId

ID_FILE_MAP = {
    "product": f"{os.getcwd()}/src/layers/domain/core/cpm_system_id/generated_ids/product_ids.json",
}

ID_CLASS_MAP = {
    "product": ProductId,
}


def generator(id_type="product"):
    id_class = ID_CLASS_MAP.get(id_type)
    generator = id_class.create()
    return generator.__root__


def open_file(id_type="product"):
    if os.path.exists(ID_FILE_MAP.get(id_type)):
        with open(ID_FILE_MAP.get(id_type), "r") as file:
            return set(json.load(file))
    return set()


def save_file(ids, id_type="product"):
    with open(ID_FILE_MAP.get(id_type), "w") as file:
        json.dump(list(ids), file)


def bulk_generator(id_count=1, id_type="product"):
    ids = open_file(id_type=id_type)
    starting_id_count = len(ids)
    while len(ids) - starting_id_count < id_count:
        ids.add(generator())
    save_file(ids, id_type)
    return ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate unique Product Ids.")
    parser.add_argument(
        "--count", type=int, default=1, help="Number of Product Ids to generate."
    )
    args = parser.parse_args()
    ids = bulk_generator(args.count)
    id_type = "product"
    print(f"Generated {id_type.capitalize()} Ids...")  # noqa
    print("========================")  # noqa
    for id in ids:
        print(id)  # noqa

    print("========================")  # noqa
