from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from models import Order, User
from schemas import OrderModel
from database import session, engine, SessionLocal
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

order_rooter = APIRouter(prefix="/order")
session = session(bind=engine)


@order_rooter.get('/')
async def order(Authorsize: AuthJWT = Depends()):
    try:
        Authorsize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")


@order_rooter.post('/make', status_code=status.HTTP_200_OK)
async def make_order(order: OrderModel, Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_order = Order(
        quantity=order.quantity,
        order_status="PENDING",
        user_id=user.id,
        product_id=order.product_id
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    response = {
        "id": new_order.id,
        "quantity": new_order.quantity,
        "order_status": new_order.order_status,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        },
        "product_id": new_order.product_id
    }
    return jsonable_encoder(response)


@order_rooter.get('/list')
async def order_list(Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
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
        orders = db.query(Order).all()
        context = [
            {
                "id": order.id,
                "quantity": order.quantity,
                "order_status": order.order_status.value,
                "user_id": order.user_id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email,
                    "is_staff": order.user.is_staff
                } if order.user else None,
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                } if order.product else None,
                "Total summa": order.quantity * order.product.price if order.product else None
            }
            for order in orders
        ]
        return jsonable_encoder(context)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only staff can view all orders")


@order_rooter.get('/{id}')
async def list_id(id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    current_user = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == current_user).first()
    if user.is_staff:
        order = db.query(Order).filter(Order.id == id).first()
        costumer_order = [
            {
                "id": order.id,
                "quantity": order.quantity,
                "order_status": order.order_status.value,
                "user_id": order.user_id,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_staff": user.is_staff
                },
                "product_id": order.product_id
            }
        ]
        return jsonable_encoder(costumer_order)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Ma'lumotlarni ko'rish uchun supper admin bo'lish kerak")


@order_rooter.get("/user/order", status_code=status.HTTP_200_OK)
async def user_order(Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    username = Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username == username).first()
    context = [
        {
            "id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.value,
            "user_id": order.user_id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email,
                "is_staff": order.user.is_staff
            } if order.user else None,
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            } if order.product else None,
            "Total summa": order.quantity * order.product.price if order.product else None
        }
        for order in user.order
    ]
    return jsonable_encoder(context)


@order_rooter.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def order_id(id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    current_user = db.query(User).filter(User.username == username).first()

    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    order = db.query(Order).filter(Order.id == id, Order.user == current_user).first()

    if order:
        order_data = {
            "id": order.id,
            "quantity": order.quantity,
            "order_status": order.order_status.value,
            "user_id": order.user_id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email,
                "is_staff": order.user.is_staff
            } if order.user else None,
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            } if order.product else None,
            "Total summa": order.quantity * order.product.price if order.product else None
        }
        return jsonable_encoder(order_data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id {id} not found")

#
# @order_rooter.get('user/order/{id}', status_code=status.HTTP_200_OK)
# async def order_id(id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
#     try:
#         Authorize.jwt_required()
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
#     username = Authorize.get_jwt_subject()
#     current_user = db.query(User).filter(User.username == username).first()
#     orders = db.query(Order).filter(Order.id == id, Order.user == current_user)
#     if orders:
#         order_data = {
#             "id": order.id,
#             "quantity": order.quantity,
#             "order_status": order.order_status.value,
#             "user_id": order.user_id,
#             "user": {
#                 "id": order.user.id,
#                 "username": order.user.username,
#                 "email": order.user.email,
#                 "is_staff": order.user.is_staff
#             } if order.user else None,
#             "product": {
#                 "id": order.product.id,
#                 "name": order.product.name,
#                 "price": order.product.price
#             } if order.product else None,
#             "Total summa": order.quantity * order.product.price if order.product else None
#         }
#         return jsonable_encoder(order_data)
#     else:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Bunday {id} id mavjud emas ")

# ____________________________________________________________________________________________________________________
#
# @order_rooter.get('/list')
# async def order_list(Authorize: AuthJWT = Depends()):
#     # Barcha buyurtmalarni ko'rish uchun
#     try:
#         Authorize.jwt_required()
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
#     current_user = Authorize.get_jwt_subject()
#     user = session.query(Order).filter(User.username == current_user).first()
#     # if user.is_staff:
#     order = session.query(Order).all()
#     context = [
#         {
#             "id": orders.id,
#             "quantity": orders.quantity,
#             "order_status": orders.order_status,
#             "user": {
#                 "id": orders.user.id,
#                 "username": orders.user.usernmae,
#                 "email": orders.user.email
#             },
#             "product_id": orders.product_id
#
#         }
#         for orders in order
#     ]
#     return jsonable_encoder(context)
#     # else:
#     #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Ma'lumotlarni faqat supper admin kora oladi")

#
# @order_rooter.post('/make', status_code=status.HTTP_200_OK)
# async def make_order(order: OrderModel, Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required()
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
#     current_user = Authorize.get_jwt_subject()
#     user = session.query(Order).filter(User.username == current_user).first()
#
#     check_order = session.query(Order).filter(Order.id == order.id).first()
#     if check_order:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bunday id mavjud")
#     new_order = Order(
#         # id=order.id,
#         quantity=order.quantity,
#         # order_status=order.order_status,
#     )
#     new_order.user = user
#     session.add(new_order)
#     session.commit()
#
#     response = {
#         "id": new_order.id,
#         "quantity": new_order.quantity,
#         "order_status": new_order.order_status,
#     }
#     return jsonable_encoder(response)
#


#
#
# @order_rooter.get('/list')
# async def order_list(Authorize: AuthJWT = Depends(), db: Session = Depends(SessionLocal)):
#     try:
#         Authorize.jwt_required()
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
#
#     current_user = Authorize.get_jwt_subject()
#     user = db.query(User).filter(User.username == current_user).first()
#
#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
#
#     # Barcha buyurtmalarni faqat is_staff foydalanuvchilar ko'rishi mumkin
#     if user.is_staff:
#         orders = db.query(Order).all()
#         context = [
#             {
#                 "id": order.id,
#                 "quantity": order.quantity,
#                 "order_status": order.order_status.value,
#                 "user_id": order.user_id,
#                 "user": {
#                     "id": user.id,
#                     "username": user.username,
#                     "email": user.email,
#                     "is_staff": user.is_staff
#                 },
#                 "product": {
#                     "id": order.product.id,
#                     "name": order.product.name,
#                     "price": order.product.price
#                 },
#                 "Total summa": order.quantity * order.product.price
#             }
#             for order in orders
#         ]
#         return jsonable_encoder(context)
#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only staff can view all orders")
