from typing import Optional
import logging
from fastapi import HTTPException, status

from repositories.auth import AuthRepository
from core.schemas.auth import (
    RegisterRequest, AuthRequest, AuthResponse, RegisterResponse,
    TotpGenerateRequest, TotpGenerateResponse, TotpVerifyRequest, TotpVerifyResponse,
    TotpConfirmRequest, TotpConfirmResponse,
    AddEmailRequest, AddEmailResponse, UpdateEmailRequest, UpdateEmailResponse,
    SendEmailConfirmationRequest, SendEmailConfirmationResponse,
    ConfirmEmailRequest, ConfirmEmailResponse
)
from core.models.users import User
from core.utils.totp import generate_totp_secret, get_totp_uri
from core.utils.email import send_email
from core.utils.templates import load_html_template
from core.utils.jwt import create_jwt_token

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def authenticate_user(self, auth_data: AuthRequest) -> AuthResponse:
        """
        Аутентификация пользователя.
        
        Args:
            auth_data: Данные для аутентификации (логин и пароль)
            
        Returns:
            AuthResponse: Результат аутентификации с информацией о пользователе
            
        Raises:
            HTTPException: Если аутентификация не удалась
        """
        logger.info(f"Authenticating user with login: {auth_data.login}")
        
        user = await self.repository.authenticate_user(auth_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль"
            )
        
        # Формируем ответ с информацией о пользователе
        email = user.email if user.is_email_confirmed else None
        response = AuthResponse(
            user_id=user.id,
            message="Аутентификация успешна",
            email=email,
            totp_enabled=user.is_totp_confirmed and user.totp_key is not None
        )
        
        logger.info(f"Successfully authenticated user: {auth_data.login}")
        return response

    async def register_user(self, register_data: RegisterRequest, user_type: str = "simple") -> RegisterResponse:
        """
        Регистрация нового пользователя.
        
        Args:
            register_data: Данные для регистрации (логин и пароль)
            user_type: Тип пользователя (по умолчанию "simple")
            
        Returns:
            RegisterResponse: Результат регистрации
            
        Raises:
            HTTPException: Если пользователь уже существует или произошла ошибка
        """
        logger.info(f"Registering new user with login: {register_data.login}")
        
        # Проверяем валидность данных
        if len(register_data.login) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Логин должен содержать минимум 2 символа"
            )
            
        if len(register_data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль должен содержать минимум 8 символов"
            )
        
        user = await self.repository.register_user(register_data, user_type)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким логином уже существует"
            )
        
        response = RegisterResponse(
            user_id=user.id,
            message=f"Пользователь {register_data.login} успешно зарегистрирован"
        )
        
        logger.info(f"Successfully registered user: {register_data.login}")
        return response

    async def get_user_by_login(self, login: str) -> Optional[User]:
        """
        Получение пользователя по логину.
        
        Args:
            login: Логин пользователя (username или email)
            
        Returns:
            Optional[User]: Модель пользователя или None, если не найден
        """
        return await self.repository.get_user_by_login(login)

    async def get_user_by_id(self, user_id: int) -> User:
        """
        Получение пользователя по ID для аутентификации.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            User: Модель пользователя
            
        Raises:
            HTTPException: Если пользователь не найден
        """
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь с id {user_id} не найден"
            )
        return user

    async def update_user_password(self, user_id: int, new_password: str) -> bool:
        """
        Обновление пароля пользователя.
        
        Args:
            user_id: ID пользователя
            new_password: Новый пароль
            
        Returns:
            bool: True, если пароль успешно обновлен
            
        Raises:
            HTTPException: Если пользователь не найден или пароль не соответствует требованиям
        """
        logger.info(f"Updating password for user id: {user_id}")
        
        # Проверяем валидность пароля
        if len(new_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пароль должен содержать минимум 8 символов"
            )
        
        # Проверяем, существует ли пользователь
        await self.get_user_by_id(user_id)
        
        success = await self.repository.update_user_password(user_id, new_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при обновлении пароля"
            )
        
        logger.info(f"Successfully updated password for user id: {user_id}")
        return True

    async def generate_totp(self, request: TotpGenerateRequest) -> TotpGenerateResponse:
        """
        Генерация TOTP для пользователя.
        
        Args:
            request: Запрос с ID пользователя
            
        Returns:
            TotpGenerateResponse: Ответ с URI для QR-кода
            
        Raises:
            HTTPException: Если пользователь не найден
        """
        logger.info(f"Generating TOTP for user id: {request.user_id}")
        
        # Проверяем, существует ли пользователь
        user = await self.get_user_by_id(request.user_id)
        
        # Генерируем новый TOTP секрет
        totp_secret = generate_totp_secret()
        
        # Сохраняем секрет в базе данных
        success = await self.repository.enable_totp(request.user_id, totp_secret)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при сохранении TOTP ключа"
            )
        
        # Генерируем URI для QR-кода
        totp_uri = get_totp_uri(totp_secret, user.username)
        
        response = TotpGenerateResponse(
            user_id=request.user_id,
            totp_uri=totp_uri,
            message="TOTP успешно сгенерирован. Отсканируйте QR-код в приложении аутентификатора."
        )
        
        logger.info(f"Successfully generated TOTP for user id: {request.user_id}")
        return response

    async def verify_totp(self, request: TotpVerifyRequest) -> TotpVerifyResponse:
        """
        Проверка TOTP кода для пользователя.
        
        Args:
            request: Запрос с ID пользователя и TOTP кодом
            
        Returns:
            TotpVerifyResponse: Результат проверки
            
        Raises:
            HTTPException: Если пользователь не найден или TOTP не настроен
        """
        logger.info(f"Verifying TOTP for user id: {request.user_id}")
        
        # Проверяем, существует ли пользователь
        user = await self.get_user_by_id(request.user_id)
        
        if not user.totp_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP не настроен для данного пользователя"
            )
        
        # Проверяем TOTP код
        is_valid = await self.repository.verify_totp(request.user_id, request.code)
        
        if is_valid:
            message = "TOTP код подтвержден"
            logger.info(f"TOTP verification successful for user id: {request.user_id}")
        else:
            message = "Неверный TOTP код"
            logger.warning(f"TOTP verification failed for user id: {request.user_id}")
        
        response = TotpVerifyResponse(
            user_id=request.user_id,
            verified=is_valid,
            message=message
        )
        
        return response

    async def confirm_totp(self, request: TotpConfirmRequest) -> TotpConfirmResponse:
        """
        Подтверждение TOTP для пользователя с проверкой кода.
        
        Args:
            request: Запрос с ID пользователя и TOTP кодом
            
        Returns:
            TotpConfirmResponse: Результат подтверждения TOTP
            
        Raises:
            HTTPException: Если пользователь не найден, TOTP не настроен или код неверный
        """
        logger.info(f"Confirming TOTP for user id: {request.user_id}")
        
        # Проверяем, существует ли пользователь
        user = await self.get_user_by_id(request.user_id)
        
        if not user.totp_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP не настроен для данного пользователя"
            )
        
        # Проверяем TOTP код перед подтверждением
        is_valid = await self.repository.verify_totp(request.user_id, request.code)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный TOTP код"
            )
        
        # Подтверждаем TOTP только после успешной проверки кода
        success = await self.repository.confirm_totp(request.user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при подтверждении TOTP"
            )
        
        response = TotpConfirmResponse(
            user_id=request.user_id,
            message="TOTP успешно подтвержден и активирован"
        )
        
        logger.info(f"Successfully confirmed TOTP for user id: {request.user_id}")
        return response

    async def add_email(self, request: AddEmailRequest) -> AddEmailResponse:
        """
        Добавление почты пользователю.
        
        Args:
            request: Запрос с ID пользователя и почтой
            
        Returns:
            AddEmailResponse: Результат добавления почты
            
        Raises:
            HTTPException: Если пользователь не найден или почта уже занята
        """
        logger.info(f"Adding email {request.email} to user id: {request.user_id}")
        
        # Проверяем, существует ли пользователь
        await self.get_user_by_id(request.user_id)
        
        # Добавляем почту через репозиторий
        user = await self.repository.add_email(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Почта уже занята другим пользователем"
            )
        
        response = AddEmailResponse(
            user_id=user.id,
            email=user.email,
            message=f"Почта {request.email} успешно добавлена. Требуется подтверждение."
        )
        
        logger.info(f"Successfully added email {request.email} to user id: {request.user_id}")
        return response

    async def update_email(self, request: UpdateEmailRequest) -> UpdateEmailResponse:
        """
        Изменение почты пользователя.
        
        Args:
            request: Запрос с ID пользователя и новой почтой
            
        Returns:
            UpdateEmailResponse: Результат изменения почты
            
        Raises:
            HTTPException: Если пользователь не найден или почта уже занята
        """
        logger.info(f"Updating email to {request.email} for user id: {request.user_id}")
        
        # Проверяем, существует ли пользователь
        await self.get_user_by_id(request.user_id)
        
        # Обновляем почту через репозиторий
        user = await self.repository.update_email(request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Почта уже занята другим пользователем"
            )
        
        response = UpdateEmailResponse(
            user_id=user.id,
            email=user.email,
            message=f"Почта успешно изменена на {request.email}. Требуется подтверждение."
        )
        
        logger.info(f"Successfully updated email to {request.email} for user id: {request.user_id}")
        return response

    async def send_email_confirmation(self, request: SendEmailConfirmationRequest) -> SendEmailConfirmationResponse:
        """
        Отправка письма для подтверждения почты.
        
        Args:
            request: Запрос с ID пользователя
            
        Returns:
            SendEmailConfirmationResponse: Результат отправки письма
            
        Raises:
            HTTPException: Если пользователь не найден или у него нет почты
        """
        logger.info(f"Sending email confirmation for user id: {request.user_id}")
        
        # Проверяем, существует ли пользователь
        user = await self.get_user_by_id(request.user_id)
        
        if not user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="У пользователя не указана почта"
            )
        
        # Создаем токен для подтверждения
        token = create_jwt_token(user.id)  # Токен без срока действия
        
        # Формируем ссылку для подтверждения
        from core.config import settings
        confirm_link = f"{settings.BASE_URL}/auth/confirm-email?user_id={user.id}&token={token}"
        
        # Загружаем HTML шаблон письма
        email_body = load_html_template("email_body_code_confirmation.html", 
                                       confirm_link=confirm_link, 
                                       static_url=settings.STATIC_URL)
                                       
        # Отправляем письмо
        success = send_email(
            to_email=user.email,
            subject="Подтверждение почты | Hash Clash",
            body=email_body
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при отправке письма"
            )
        
        response = SendEmailConfirmationResponse(
            user_id=user.id,
            message=f"Письмо для подтверждения почты отправлено на {user.email}"
        )
        
        logger.info(f"Successfully sent email confirmation for user id: {request.user_id}")
        return response

    async def confirm_email(self, request: ConfirmEmailRequest) -> ConfirmEmailResponse:
        """
        Подтверждение почты пользователя.
        
        Args:
            request: Запрос с ID пользователя и токеном
            
        Returns:
            ConfirmEmailResponse: Результат подтверждения
            
        Raises:
            HTTPException: Если пользователь не найден или токен неверный
        """
        logger.info(f"Confirming email for user id: {request.user_id}")
        
        # Проверяем, существует ли пользователь
        user = await self.get_user_by_id(request.user_id)
        
        # TODO: Здесь можно добавить проверку токена, если нужно
        # Пока что просто подтверждаем почту
        
        success = await self.repository.confirm_email(request.user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ошибка при подтверждении почты"
            )
        
        response = ConfirmEmailResponse(
            user_id=user.id,
            message="Почта успешно подтверждена"
        )
        
        logger.info(f"Successfully confirmed email for user id: {request.user_id}")
        return response
