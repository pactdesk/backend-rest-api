from pydantic import BaseModel

from draftmaster.models.domain.base import Section


class Contract(BaseModel):
    parties: Section
    considerations: Section
    agreements: Section
    signatures: Section
