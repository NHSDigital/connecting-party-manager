"""
Generate the lambda global variables (i.e. cache) for
both the load_bulk and load_update workers
"""

from event.environment import BaseEnvironment


class LoadWorkerEnvironment(BaseEnvironment):
    ETL_BUCKET: str
    TABLE_NAME: str

    def s3_path(self, key) -> str:
        return f"s3://{self.ETL_BUCKET}/{key}"
