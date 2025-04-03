from enum import Enum


class IndustryCodeEnum(str, Enum):
    AGRO = "agro"
    CONSUMER = "consump"
    FINANCIALS = "fincial"
    INDUSTRIALS = "indus"
    PROPERTY = "propcon"
    RESOURCES = "resource"
    SERVICES = "service"
    TECH = "tech"
