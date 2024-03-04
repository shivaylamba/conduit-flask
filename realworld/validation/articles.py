from pydantic import BaseModel, model_validator, ValidationError

class CreateArticleRequest(BaseModel):
    title: str
    description: str
    body: str
    tagList: list[str]

    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
            
        return fields
    
class Article(BaseModel):
    title: str
    description: str
    body: str
    tag_list: list[str]
    created_at: str
    updated_at: str
    favorited: list[str]
    article_id: str
    slug : str
    author : object

class CreateArticleResponse(BaseModel):
    article: Article

class GetArticlesResponse(BaseModel):
    articles: list[Article]

class GetArticleResponse(BaseModel):
    article: Article

class UpdateArticleRequest(BaseModel):
    article_id: str
    fields: dict

    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
            
        return fields
    
class UpdateArticleResponse(BaseModel):
    message: str

class DeleteArticleRequest(BaseModel):
    article_id: str

    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
            
        return fields

class DeleteArticleResponse(BaseModel):
    message: str

class FavoriteArticleRequest(BaseModel):
    article_id: str

    @model_validator(mode='before')
    def validate_all(cls, fields):
        for key in fields.keys():
            if not fields[key]:
                raise ValidationError(f"Validation failed for {key}")
            
        return fields

class FavoriteArticleResponse(BaseModel):
    message: str

class GetTagsResponse(BaseModel):
    tags: list[str]