from pydantic import BaseModel


class DonationNotifyRequest(BaseModel):
    product_id: int
