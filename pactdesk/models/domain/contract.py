from pydantic import BaseModel

from pactdesk.models.domain.base import Section


class Contract(BaseModel):
    parties: Section
    considerations: Section
    agreements: Section
    signatures: Section
