from pydantic import BaseModel, model_validator, ValidationError

class CreateCommentRequest(BaseModel):
    body: str
    article_id: str

    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
            
        return fields
    
class Comment(BaseModel):
    comment_id: int
    article_id: int
    body: str
    created_at: str

class CreateCommentResponse(BaseModel):
    comment: Comment

class GetCommentsResponse(BaseModel):
    comments: list[Comment]

class DeleteCommentResponse(BaseModel):
    message: str