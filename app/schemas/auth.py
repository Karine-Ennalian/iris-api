from pydantic import BaseModel, Field


class OtpRequestIn(BaseModel):
    patient_id: str


class OtpRequestOut(BaseModel):
    success: bool = True
    challenge_id: str
    phone_last_digits: str | None = None
    expires_in: int
    dev_code: str | None = None


class OtpVerifyIn(BaseModel):
    challenge_id: str
    code: str = Field(min_length=4, max_length=10)


class OtpVerifyOut(BaseModel):
    success: bool
    authenticated: bool
    access_token: str | None = None
    token_type: str | None = None
    expires_in: int | None = None
    error: str | None = None
    message: str | None = None
