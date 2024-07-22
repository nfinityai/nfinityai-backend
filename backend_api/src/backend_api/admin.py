from fastapi.middleware import Middleware
from fastapi.requests import Request
from fastapi.responses import Response
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.contrib.sqla import Admin
from starlette_admin.exceptions import FormValidationError, LoginFailed

from backend_api.backend.config import get_settings
from backend_api.backend.session import engine

settings = get_settings()

users = {
    settings.admin_username: {
        "name": "Administrator",
        "avatar": None,
        "roles": ["read", "create", "edit", "delete", "action_make_published"],
    }
}


class AdminAuthProvider(AuthProvider):
    """
    This is for demo purpose, it's not a better
    way to save and validate user credentials
    """

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        if len(username) < 3:
            """Form data validation"""
            raise FormValidationError(
                {"username": "Ensure username has at least 03 characters"}
            )

        if username == settings.admin_username and password == settings.admin_password:
            """Save `username` in session"""
            request.session.update({"username": username})
            return response

        raise LoginFailed("Invalid username or password")

    async def is_authenticated(self, request) -> bool:
        if request.session.get("username", None) == settings.admin_username:
            """
            Save current `user` object in the request state. Can be used later
            to restrict access to connected user.
            """
            request.state.user = users.get(request.session["username"])
            return True

        return False

    def get_admin_config(self, request: Request) -> AdminConfig:
        user = request.state.user  # Retrieve current user
        # Update app title according to current_user
        custom_app_title = "Hello, " + user["name"] + "!"
        return AdminConfig(
            app_title=custom_app_title,
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user  # Retrieve current user
        return AdminUser(username=user["name"])

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response


site = Admin(
    engine,
    title="Nfinity Admin",
    base_url="/admin",
    auth_provider=AdminAuthProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key=settings.secret_key)],
)
