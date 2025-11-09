from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from core.schemas.auth import (
    RegisterRequest, AuthRequest, AuthResponse, RegisterResponse,
    TotpGenerateRequest, TotpGenerateResponse, TotpVerifyRequest, TotpVerifyResponse,
    TotpConfirmRequest, TotpConfirmResponse,
    AddEmailRequest, AddEmailResponse, UpdateEmailRequest, UpdateEmailResponse,
    SendEmailConfirmationRequest, SendEmailConfirmationResponse,
    ConfirmEmailRequest, ConfirmEmailResponse
)
from api.deps import get_auth_service
from services.auth import AuthService
from core.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"description": "Authentication failed"}}
)

@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate user",
    description="Authenticate user with login and password",
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Invalid credentials"},
        400: {"description": "Invalid request data"}
    }
)
async def login(
    auth_data: AuthRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user with login and password:
    - Validates user credentials
    - Returns authentication result with user info
    - Supports both username and email as login
    """
    return await auth_service.authenticate_user(auth_data)

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user in the system",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Invalid registration data or user already exists"}
    }
)
async def register(
    register_data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user:
    - Validates registration data
    - Checks for existing users
    - Creates new user account
    - Returns registration confirmation
    """
    return await auth_service.register_user(register_data)

@router.post(
    "/totp/generate",
    response_model=TotpGenerateResponse,
    summary="Generate TOTP for user",
    description="Generate TOTP secret and QR code URI for user",
    responses={
        200: {"description": "TOTP generated successfully"},
        404: {"description": "User not found"},
        500: {"description": "Error saving TOTP key"}
    }
)
async def generate_totp(
    request: TotpGenerateRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Generate TOTP for user:
    - Creates new TOTP secret
    - Saves secret to database
    - Returns QR code URI for authenticator app
    - TOTP requires separate confirmation after verification
    """
    return await auth_service.generate_totp(request)

@router.post(
    "/totp/verify",
    response_model=TotpVerifyResponse,
    summary="Verify TOTP code",
    description="Verify TOTP code for user",
    responses={
        200: {"description": "TOTP verification completed"},
        400: {"description": "TOTP not configured or invalid code"},
        404: {"description": "User not found"}
    }
)
async def verify_totp(
    request: TotpVerifyRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify TOTP code for user:
    - Validates TOTP code against user's secret
    - Returns verification result
    - Supports time window tolerance
    """
    return await auth_service.verify_totp(request)

@router.post(
    "/totp/confirm",
    response_model=TotpConfirmResponse,
    summary="Confirm TOTP setup",
    description="Confirm TOTP setup with code verification",
    responses={
        200: {"description": "TOTP confirmed successfully"},
        400: {"description": "TOTP not configured or invalid code"},
        404: {"description": "User not found"},
        500: {"description": "Error confirming TOTP"}
    }
)
async def confirm_totp(
    request: TotpConfirmRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Confirm TOTP setup for user:
    - Requires TOTP to be generated first
    - Validates the provided TOTP code
    - Sets is_totp_confirmed to true only if code is valid
    - Activates TOTP authentication for the user
    """
    return await auth_service.confirm_totp(request)

@router.post(
    "/email/add",
    response_model=AddEmailResponse,
    summary="Add email to user",
    description="Add email address to user account",
    responses={
        200: {"description": "Email added successfully"},
        400: {"description": "Email already taken or invalid request"},
        404: {"description": "User not found"}
    }
)
async def add_email(
    request: AddEmailRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Add email to user account:
    - Validates email format
    - Checks if email is already taken
    - Sets email confirmation status to false
    - Returns confirmation message
    """
    return await auth_service.add_email(request)

@router.put(
    "/email/update",
    response_model=UpdateEmailResponse,
    summary="Update user email",
    description="Update user email address",
    responses={
        200: {"description": "Email updated successfully"},
        400: {"description": "Email already taken or invalid request"},
        404: {"description": "User not found"}
    }
)
async def update_email(
    request: UpdateEmailRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update user email address:
    - Validates new email format
    - Checks if email is already taken by another user
    - Resets email confirmation status to false
    - Returns confirmation message
    """
    return await auth_service.update_email(request)

@router.post(
    "/send-email-confirmation",
    response_model=SendEmailConfirmationResponse,
    summary="Send email confirmation",
    description="Send email confirmation to user",
    responses={
        200: {"description": "Email confirmation sent successfully"},
        400: {"description": "User not found or no email set"},
        500: {"description": "Error sending email"}
    }
)
async def send_email_confirmation(
    request: SendEmailConfirmationRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Send email confirmation to user:
    - Validates user exists and has email
    - Generates confirmation token
    - Sends email with confirmation link
    - Returns confirmation message
    """
    return await auth_service.send_email_confirmation(request)
