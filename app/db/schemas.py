from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ReactionType(str, Enum):
    like = "like"
    dislike = "dislike"

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    avatar_url: Optional[str] = None

class User(UserBase):
    id: int
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    description: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class Post(PostBase):
    id: int
    image_url: str
    user_id: int
    created_at: datetime
    user: User
    
    class Config:
        from_attributes = True

class PostWithDetails(Post):
    comments: List["Comment"] = []
    like_count: int = 0
    dislike_count: int = 0

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    user: User
    
    class Config:
        from_attributes = True

class ReactionCreate(BaseModel):
    reaction_type: ReactionType

class Reaction(BaseModel):
    id: int
    user_id: int
    post_id: int
    reaction_type: ReactionType
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReactionSummary(BaseModel):
    like_count: int
    dislike_count: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

PostWithDetails.model_rebuild()