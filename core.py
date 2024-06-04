from fastapi import FastAPI
from auth import auth_rooter
from order import order_rooter
from fastapi_jwt_auth import AuthJWT
from schemas import LoginMadel, Settings
from product import product_rooter

app = FastAPI()
app.include_router(auth_rooter)
app.include_router(order_rooter)
app.include_router(product_rooter)


@AuthJWT.load_config
def get_cofig():
    return Settings()


@app.get('/')
async def root():
    return {"massage": "Asosiy sahifa"}
