from pydantic import BaseModel, model_validator, ValidationError

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str

    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
            
        return fields

class NestedRegisterResponse(BaseModel):
    username: str
    email: str
    token: str

class RegisterResponse(BaseModel):
    user: NestedRegisterResponse


class LoginRequest(BaseModel):
    email: str
    password: str

    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
            
        return fields
    

class CurrentUserRequest(BaseModel):
    email: str
    password: str

    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
            
        return fields
    
class ErrorResponse(BaseModel):
    error: str