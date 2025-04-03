from enum import Enum


class RoleEnum(str, Enum):
    CLIENT = "client"
    BACKEND = "backend"
    ML_SERVER = "ml_server"
