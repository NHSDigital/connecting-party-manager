def validate_tags(tags):
    assert tags == []  # The tags field is dropped due to being chunky


def validate_product_result_body(result_body, products):
    if isinstance(products, dict):  # single product
        products = [products]
    assert sorted(result_body, key=lambda d: d["id"]) == sorted(
        products, key=lambda d: d["id"]
    )
