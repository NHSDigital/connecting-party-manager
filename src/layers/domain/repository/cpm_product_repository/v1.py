from attr import asdict
from domain.core.cpm_product import (
    CpmProduct,
    CpmProductCreatedEvent,
    CpmProductDeletedEvent,
    CpmProductKeyAddedEvent,
)
from domain.core.product_key import ProductKey
from domain.repository.keys import TableKey
from domain.repository.repository import Repository


class CpmProductRepository(Repository[CpmProduct]):
    def __init__(self, table_name: str, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=CpmProduct,
            dynamodb_client=dynamodb_client,
            parent_table_keys=(TableKey.PRODUCT_TEAM,),
            table_key=TableKey.CPM_PRODUCT,
        )

    def read(self, product_team_id: str, id: str):
        return super()._read(parent_ids=(product_team_id,), id=id)

    def search(self, product_team_id: str):
        return super()._search(parent_ids=(product_team_id,))

    def handle_CpmProductCreatedEvent(self, event: CpmProductCreatedEvent):
        return self.create_index(
            id=event.id,
            parent_key_parts=(event.product_team_id,),
            data=asdict(event),
            root=True,
        )

    def handle_CpmProductKeyAddedEvent(self, event: CpmProductKeyAddedEvent):
        # Create a copy of the Product indexed against the new key
        create_transaction = self.create_index(
            id=event.new_key.key_value,
            parent_key_parts=(event.product_team_id,),
            data=asdict(event),
            root=False,
        )

        # Update the value of "keys" on all other copies of this Device
        product_keys = {ProductKey(**key) for key in event.keys}
        product_keys_before_update = product_keys - {event.new_key}
        update_transactions = self.update_indexes(
            id=event.id,
            keys=product_keys_before_update,
            data={"keys": event.keys, "updated_on": event.updated_on},
        )
        return [create_transaction] + update_transactions

    def handle_CpmProductDeletedEvent(self, event: CpmProductDeletedEvent):
        inactive_root_copy_transaction = self.create_index(
            id=event.id,
            parent_key_parts=(event.product_team_id,),
            data=asdict(event),
            root=True,
            table_key=TableKey.CPM_PRODUCT_STATUS,
        )

        keys = {ProductKey(**k).key_value for k in event.keys}
        inactive_key_indexes_copy_transactions = [
            self.create_index(
                id=key,
                parent_key_parts=(event.product_team_id,),
                data=asdict(event),
                root=False,
                table_key=TableKey.CPM_PRODUCT_STATUS,
            )
            for key in keys
        ]

        original_indexes_delete_transactions = [
            self.delete_index(key) for key in (*keys, event.id)
        ]
        return (
            [inactive_root_copy_transaction]
            + inactive_key_indexes_copy_transactions
            + original_indexes_delete_transactions
        )


class InactiveCpmProductRepository(Repository[CpmProduct]):
    """Read-only repository"""

    def __init__(self, table_name, dynamodb_client):
        super().__init__(
            table_name=table_name,
            model=CpmProduct,
            dynamodb_client=dynamodb_client,
            parent_table_keys=(TableKey.PRODUCT_TEAM,),
            table_key=TableKey.CPM_PRODUCT_STATUS,
        )

    def read(self, product_team_id: str, id: str):
        return self._read(parent_ids=(product_team_id,), id=id)