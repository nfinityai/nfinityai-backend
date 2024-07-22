from starlette_admin.contrib.sqla import Admin
from backend_api.backend.session import engine


site = Admin(engine)
