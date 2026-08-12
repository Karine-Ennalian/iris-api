import re


def digits_only(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def validate_cns_format(cns: str) -> str:
    normalized = digits_only(cns)
    if len(normalized) != 15:
        raise ValueError("O CNS deve conter exatamente 15 dígitos.")
    return normalized


def mask_cpf(cpf: str | None) -> str | None:
    if not cpf:
        return None
    digits = digits_only(cpf)
    if len(digits) != 11:
        return "***.***.***-**"
    return f"***.***.{digits[6:9]}-{digits[9:11]}"


def phone_last_digits(phone: str | None, quantity: int = 2) -> str | None:
    if not phone:
        return None
    digits = digits_only(phone)
    return digits[-quantity:] if digits else None


def first_name(name: str | None) -> str | None:
    if not name:
        return None
    return name.strip().split()[0]
