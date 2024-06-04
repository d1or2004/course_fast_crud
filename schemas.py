from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]
    #
    # class Config:
    #     orm_mode = True
    #     schema_extra = {
    #         "example": {
    #             'username': "diordev",
    #             'email': 'diordev@gmail.com',
    #             'password': 'diordev2004',
    #             'is_staff': False,
    #             'is_active': True
    #         }
    #     }


class Settings(BaseModel):
    # import secrets
    # secrets.token_hex()
    authjwt_secret_key: str = "54c50460565fbfdc699b7a50f138b0755b7e6985e5f2180aa8609b01f36205c4"


class LoginMadel(BaseModel):
    username: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str] = "PENDING"
    user_id: Optional[int]
    product_id: Optional[int]


class OrderStatusModel(BaseModel):
    order_status: Optional[str] = "PENDING"


class ProductModel(BaseModel):
    id: Optional[int]
    name: str
    price: int
