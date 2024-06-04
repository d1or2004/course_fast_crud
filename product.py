from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from models import Order, User, Product
from schemas import ProductModel
from database import session, engine, SessionLocal
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

product_rooter = APIRouter(prefix="/product")
session = session(bind=engine)


@product_rooter.get("/")
async def product(Authorsize: AuthJWT = Depends()):
    try:
        Authorsize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")


@product_rooter.post("/make", status_code=status.HTTP_200_OK)
async def make_product(product: ProductModel, Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_product = Product(
        name=product.name,
        price=product.price
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    response = {
        "id": new_product.id,
        "name": new_product.name,
        "price": new_product.price
    }
    data = {
        "code": 200,
        "msg": "Successfully",
        "data": response
    }
    return jsonable_encoder(data)


@product_rooter.get('/list')
async def product_list(Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Barcha buyurtmalarni faqat is_staff foydalanuvchilar ko'rishi mumkin
    if user.is_staff:
        product = db.query(Product).all()
        context = [
            {
                "id": new.id,
                "name": new.name,
                "price": new.price
            }
            for new in product
        ]
        return jsonable_encoder(context)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only staff can view all product")
