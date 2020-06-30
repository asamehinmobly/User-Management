import uvicorn
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from fastapi import FastAPI, status, Depends

from starlette_context.plugins import Plugin

from entrypoints.fast_api.errors.http_error import http_error_handler
from entrypoints.fast_api.errors.validation_error import http422_error_handler
from entrypoints.fast_api.request_model.model import LoginInRequest, CreateUserInResponse, CreateUserInRequest, \
    ResetPasswordInRequest, SendResetEmailInRequest, LoginInResponse, RefreshTokenInRequest, UpdateDeviceTokenInRequest, \
    GetTestUserTokenInRequest, SendResetEmailInResponse, UserDataInResponse
from config import DEBUG, PROJECT_NAME, VERSION, API_HOST, API_PORT
from domain import commands
from middlewares.oauth_checker import OauthChecker
from service_layer.handlers import InvalidEmail
import views
from fastapi_contrib.tracing.middlewares import OpentracingMiddleware
from fastapi_contrib.tracing.utils import setup_opentracing

from utils.bus_singleton import BusSingleton
from utils.reset_token import create_user_token, create_refresh_token

from starlette.requests import Request
from starlette_context.middleware import ContextMiddleware


def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)
    # application.include_router(api_router, prefix=API_PREFIX)
    # application.add_event_handler("startup", setup_jaeger(application))

    return application


class MessagePlugin(Plugin):
    key = 'Message'


app = get_application()

app.add_middleware(
    ContextMiddleware,
    plugins=(
        MessagePlugin(),
    )
)


@app.on_event('startup')
async def startup():
    setup_opentracing(app)
    app.add_middleware(OpentracingMiddleware)


bus = BusSingleton.get_instance()

admin_checker = OauthChecker(auth=True, auth_type="admin")
user_checker = OauthChecker(auth=True, auth_type="user")


@app.post("/user/create", response_model=CreateUserInResponse, status_code=status.HTTP_201_CREATED)
def create_user(request: Request, create_data: CreateUserInRequest,
                auth_checker_response: dict = Depends(admin_checker)):
    try:
        cmd = commands.CreateUser(user_data=create_data.user_data, app_id=auth_checker_response['app_id'])
        bus.handle(cmd)

        create_data.device_data.user_id = cmd.user_id
        cmd = commands.AttachDeviceToUser(device_data=create_data.device_data)
        bus.handle(cmd)

        return views.user_create_response(email=create_data.user_data.email,
                                          app_id=auth_checker_response['app_id'],
                                          login_type=create_data.user_data.external, uow=bus.uow)

    except InvalidEmail as e:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.post("/user/login/", status_code=status.HTTP_200_OK, response_model=LoginInResponse)
def login(login_request_data: LoginInRequest, auth_checker_response: dict = Depends(admin_checker)):
    email = login_request_data.login_data.email
    pwd = login_request_data.login_data.password
    app_id = auth_checker_response['app_id']

    if not (email and pwd):
        raise HTTPException(status_code=403, detail="error message")

    user_data = views.check_login(email=email, app_id=app_id, password=pwd, uow=bus.uow)
    user_data.external = views.get_external(user_data.external)

    login_request_data.device_data.user_id = user_data.id
    cmd = commands.AttachDeviceToUser(device_data=login_request_data.device_data)
    bus.handle(cmd)

    return LoginInResponse(
        user_data=user_data, user_token=create_user_token(user_data.__dict__),
        refresh_token=create_refresh_token(user_data.user_id, app_id)
    )


@app.get("/user/check-token", status_code=status.HTTP_200_OK)
def check_token(auth_checker_response: dict = Depends(user_checker)):
    try:
        user = views.get_user(uow=bus.uow, user_id=auth_checker_response['user_id'],
                              app_id=auth_checker_response['app_id'])
        change_pass_on = user["change_pass_time"]
        output = {"message": "token valid"}
        un_auth_output = {"message": "token invalid"}
        if change_pass_on is None:
            return output
        if change_pass_on > auth_checker_response['change_pass_time']:
            return un_auth_output
        else:
            return output
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.post("/user/send-reset-email", response_model=SendResetEmailInResponse, status_code=status.HTTP_200_OK)
def send_reset_email(request: SendResetEmailInRequest, auth_checker_response: dict = Depends(admin_checker)):
    try:
        cmd = commands.SendResetEmail(email=request.email, app_id=auth_checker_response['app_id'])
        bus.handle(cmd)
        return SendResetEmailInResponse(email=request.email, access_token=cmd.token_encoded,
                                        app_id=auth_checker_response['app_id'])
    except InvalidEmail as e:
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.post("/user/reset-password", response_model=UserDataInResponse, status_code=status.HTTP_200_OK)
def reset_password(reset_password_data: ResetPasswordInRequest, email: str, token: str,
                   auth_checker_response: dict = Depends(admin_checker)):
    try:
        cmd = commands.ResetPassword(token=token, email=email, new_password=reset_password_data.new_password,
                                     app_id=auth_checker_response['app_id'])
        bus.handle(cmd)
        return views.reset_password_response(email=email, app_id=auth_checker_response['app_id'], uow=bus.uow)
    except InvalidEmail as e:
        raise HTTPException(status_code=400, detail="Email not found")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.post("/user/refresh/token", status_code=status.HTTP_200_OK)
def refresh_token(refresh_token_data: RefreshTokenInRequest, auth_checker_response: dict = Depends(admin_checker)):
    try:
        cmd = commands.RefreshToken(token=refresh_token_data.token, app_id=auth_checker_response['app_id'])
        bus.handle(cmd)
    except InvalidEmail as e:
        raise HTTPException(status_code=400, detail="Email not found")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@app.post("/user/update-device-token", status_code=status.HTTP_201_CREATED)
def update_device_token(update_device_token_data: UpdateDeviceTokenInRequest,
                        auth_checker_response: dict = Depends(user_checker)):
    try:
        cmd = commands.UpdateDeviceToken(device_id=update_device_token_data.device_id,
                                         device_token=update_device_token_data.device_token)
        bus.handle(cmd)
    except InvalidEmail as e:
        raise HTTPException(status_code=400, detail="Email not found")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    return {"status": "Done"}


# ----------------------------------------------------------------------------------
# Dashboard
# ----------------------------------------------------------------------------------

@app.get("/users/list", status_code=status.HTTP_200_OK)
def get_app_users(page_number: int, per_page: int, request: Request, keyword: str = None, type: str = None,
                  order: str = None, order_type: str = None, auth_checker_response: dict = Depends(admin_checker)):
    try:
        users = views.get_app_users(uow=bus.uow, app_id=auth_checker_response['app_id'],
                                    page=page_number, per_page=per_page, search_type=type, search_keyword=keyword,
                                    order=order, order_type=order_type)
    except InvalidEmail as e:
        raise HTTPException(status_code=400, detail="Email not found")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    return users


@app.get("/users/export", status_code=status.HTTP_200_OK)
def export_app_users(auth_checker_response: dict = Depends(admin_checker)):
    try:
        cmd = commands.ExportAppUsers(app_id=auth_checker_response['app_id'], user=auth_checker_response['user'])
        bus.handle(cmd)
    except InvalidEmail as e:
        raise HTTPException(status_code=400, detail="Email not found")
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    return {"status": True}


@app.get("/users/get-external-users", status_code=status.HTTP_200_OK)
def get_external_users(user_type: str = None, auth_checker_response: dict = Depends(admin_checker)):
    try:
        users_ids = views.get_external_users(uow=bus.uow, app_id=auth_checker_response['app_id'], user_type=user_type)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    return users_ids


@app.get("/users/external/count", status_code=status.HTTP_200_OK)
def get_count_external_users(auth_checker_response: dict = Depends(admin_checker)):
    try:
        count = views.get_count_external_users(uow=bus.uow, app_id=auth_checker_response['app_id'])
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    return count


@app.post("/users/get_user_token", status_code=status.HTTP_200_OK)
def get_test_user_token(request: GetTestUserTokenInRequest, auth_checker_response: dict = Depends(admin_checker)):
    try:
        user = views.get_user(uow=bus.uow, user_id=request.user_id, app_id=auth_checker_response['app_id'])
        data = {"token": create_user_token(user)}
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    return data


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
