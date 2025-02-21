from attr import asdict
from domain.core.cpm_product import (
    CpmProduct,
    CpmProductCreatedEvent,
    CpmProductDeletedEvent,
    CpmProductKeyAddedEvent,
)
from domain.core.enum import EntityType
from domain.core.product_key import ProductKey
from domain.repository.cpm_repository import Repository
from domain.repository.keys import TableKey


class CpmProductRepository(Repository[CpmProduct]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=CpmProduct,
            dynamodb_client=dynamodb_client,
            parent_table_keys=(TableKey.PRODUCT_TEAM,),
            table_key=TableKey.CPM_PRODUCT,
        )

    def read(self, product_team_id: str, id: str, status: str = "active"):
        return super()._read(parent_ids=(product_team_id,), id=id, status=status)

    def search_by_product_team(
        self, product_team_id: str, status: str
    ) -> list[CpmProduct]:
        """Search for products under a given Product Team."""
        return super()._search(
            parent_ids=(TableKey.PRODUCT_TEAM.key(product_team_id),),
            sk_prefix="P#",
            status=status,
        )

    def search_by_organisation(
        self, organisation_code: str, status: str
    ) -> list[CpmProduct]:
        """Search for products under a given Organisation using idx_gsi_read_2."""
        self.parent_table_keys = (TableKey.ORG_CODE,)
        return super()._search(
            parent_ids=(TableKey.ORG_CODE.key(organisation_code),),
            sk_prefix="P#",
            gsi="idx_gsi_read_2",
            status=status,
        )

    def handle_CpmProductCreatedEvent(self, event: CpmProductCreatedEvent):
        return self.create_index(
            id=event.id,
            parent_key_parts=(event.product_team_id,),
            data=asdict(event),
            root=True,
            row_type=EntityType.PRODUCT,
        )

    def handle_CpmProductKeyAddedEvent(self, event: CpmProductKeyAddedEvent):
        # Create a copy of the Product indexed against the new key
        new_key = ProductKey(**event.new_key)
        # Update the value of "keys" on all other copies of this Device
        product_keys = {ProductKey(**key) for key in event.keys}
        product_keys_before_update = product_keys - {new_key}
        update_transactions = self.update_indexes(
            pk=TableKey.PRODUCT_TEAM.key(event.product_team_id),
            id=event.id,
            keys=product_keys_before_update,
            data={"keys": event.keys, "updated_on": event.updated_on},
        )
        return update_transactions

    def handle_CpmProductDeletedEvent(self, event: CpmProductDeletedEvent):
        return self.update_indexes(
            pk=TableKey.PRODUCT_TEAM.key(event.product_team_id),
            id=event.id,
            keys=event.keys,
            data=asdict(event),
        )
