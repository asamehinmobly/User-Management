from pydantic import BaseModel


class UserData(BaseModel):
    email: str


class CreateUserData(UserData):
    name: str
    phone: str
    external: str
    password: str


class LoginData(UserData):
    password: str


class DeviceData(BaseModel):
    user_id: int = None
    device_id: str
    device_token: str
    device_type: str


class UserDataResponse(UserData):
    external: str = None
    user_id: str
    name: str
    id: int
    province: str = None
    active: int
    firebase_id: str
    phone: str
    app_id: int


class CreateUserInRequest(BaseModel):
    user_data: CreateUserData
    device_data: DeviceData


class UserDataInResponse(UserDataResponse):
    FNAME: str = ""
    LNAME: str = ""
    PROVINCE: str = ""


class CreateUserInResponse(BaseModel):
    user_data: UserDataInResponse
    user_token: str
    refresh_token: str


class LoginInRequest(BaseModel):
    login_data: LoginData
    device_data: DeviceData


class LoginInResponse(BaseModel):
    user_data: UserDataResponse
    user_token: str
    refresh_token: str


class SendResetEmailInRequest(UserData):
    pass


class SendResetEmailInResponse(UserData):
    access_token: str
    app_id: int


class ResetPasswordInRequest(BaseModel):
    new_password: str


class RefreshTokenInRequest(BaseModel):
    token: str


class UpdateDeviceTokenInRequest(BaseModel):
    device_id: str
    device_token: str


class GetTestUserTokenInRequest(BaseModel):
    user_id: str
