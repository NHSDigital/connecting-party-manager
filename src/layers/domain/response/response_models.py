from domain.core.aggregate_root import AggregateRoot


class SearchResponse[T](AggregateRoot):
    results: list[T]


class SearchProductResponse(SearchResponse[dict]):
    """Wrapper for grouping products by organisation and product team."""

    def __init__(self, products: list[dict]):
        grouped_products = self._group_products(products)
        super().__init__(results=grouped_products)

    def _group_products(self, products: list[dict]) -> list[dict]:
        organisations = {}

        product_dicts = [product.state() for product in products]

        for product in product_dicts:
            org_code = product["ods_code"]
            team_id = product["product_team_id"]

            if org_code not in organisations:
                organisations[org_code] = {"org_code": org_code, "product_teams": {}}

            if team_id not in organisations[org_code]["product_teams"]:
                organisations[org_code]["product_teams"][team_id] = {
                    "product_team_id": team_id,
                    "products": [],
                }

            organisations[org_code]["product_teams"][team_id]["products"].append(
                product
            )

        # Convert to final structured format
        return sorted(
            [
                {
                    "org_code": org["org_code"],
                    "product_teams": sorted(
                        list(org["product_teams"].values()),
                        key=lambda team: team["product_team_id"],
                    ),
                }
                for org in organisations.values()
            ],
            key=lambda org: org["org_code"],
        )
