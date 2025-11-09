from pydantic import EmailStr
from .base import BaseSchema

class RegisterRequest(BaseSchema):
    login: str
    password: str

class RegisterResponse(BaseSchema):
    user_id: int
    message: str | None = None

class AuthRequest(BaseSchema):
    login: str
    password: str

class AuthResponse(BaseSchema):
    user_id: int
    message: str | None = None
    email: EmailStr | None = None
    totp_enabled: bool | None = None

class TotpGenerateRequest(BaseSchema):
    user_id: int

class TotpGenerateResponse(BaseSchema):
    user_id: int
    totp_uri: str
    message: str | None = None

class TotpVerifyRequest(BaseSchema):
    user_id: int
    code: str

class TotpVerifyResponse(BaseSchema):
    user_id: int
    verified: bool
    message: str | None = None

class AddEmailRequest(BaseSchema):
    user_id: int
    email: EmailStr

class AddEmailResponse(BaseSchema):
    user_id: int
    email: EmailStr
    message: str | None = None

class UpdateEmailRequest(BaseSchema):
    user_id: int
    email: EmailStr

class UpdateEmailResponse(BaseSchema):
    user_id: int
    email: EmailStr
    message: str | None = None

class TotpConfirmRequest(BaseSchema):
    user_id: int
    code: str

class TotpConfirmResponse(BaseSchema):
    user_id: int
    message: str | None = None

class SendEmailConfirmationRequest(BaseSchema):
    user_id: int

class SendEmailConfirmationResponse(BaseSchema):
    user_id: int
    message: str | None = None

class ConfirmEmailRequest(BaseSchema):
    user_id: int
    token: str

class ConfirmEmailResponse(BaseSchema):
    user_id: int
    message: str | None = None