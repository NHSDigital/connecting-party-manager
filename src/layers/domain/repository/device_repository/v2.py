class DeviceRepository(Repository[Device]):
    def __init__(self):
        super().__init__()

    def query_by_tag(self, **kwargs):
        return dict(nhs_as_svc_ia="Boo")
