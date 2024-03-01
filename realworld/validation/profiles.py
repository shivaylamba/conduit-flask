from pydantic import BaseModel, model_validator, ValidationError

class FollowUnfollowRequest(BaseModel):
    action: str
    followed_username: str

class FollowUnfollowResponse(BaseModel):
    message: str