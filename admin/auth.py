"""
Аутентификация админ-панели.
"""
from fastapi import Request
from sqladmin.authentication import AuthenticationBackend

from core.config import settings


class AdminAuth(AuthenticationBackend):
    """
    Класс аутентификации для админ-панели.
    Проверяет логин и пароль из переменных окружения.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session.update({"authenticated": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get("authenticated", False)
