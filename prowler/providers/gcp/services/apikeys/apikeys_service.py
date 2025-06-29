from pydantic.v1 import BaseModel

from prowler.lib.logger import logger
from prowler.providers.gcp.gcp_provider import GcpProvider
from prowler.providers.gcp.lib.service.service import GCPService


class APIKeys(GCPService):
    def __init__(self, provider: GcpProvider):
        super().__init__(__class__.__name__, provider, api_version="v2")

        self.keys = []
        self._get_keys()

    def _get_keys(self):
        for project_id in self.project_ids:
            try:
                request = (
                    self.client.projects()
                    .locations()
                    .keys()
                    .list(
                        parent=f"projects/{project_id}/locations/global",
                    )
                )
                while request is not None:
                    response = request.execute()

                    for key in response.get("keys", []):
                        self.keys.append(
                            Key(
                                name=key["displayName"],
                                id=key["uid"],
                                creation_time=key["createTime"],
                                restrictions=key.get("restrictions", {}),
                                project_id=project_id,
                            )
                        )

                    request = (
                        self.client.projects()
                        .locations()
                        .keys()
                        .list_next(previous_request=request, previous_response=response)
                    )
            except Exception as error:
                logger.error(
                    f"{error.__class__.__name__}[{error.__traceback__.tb_lineno}]: {error}"
                )


class Key(BaseModel):
    name: str
    id: str
    creation_time: str
    restrictions: dict
    project_id: str
