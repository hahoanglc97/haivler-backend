from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from ..db import models, schemas

class PostService:
    @staticmethod
    def get_posts_with_reactions(
        db: Session, 
        skip: int = 0, 
        limit: int = 10,
        sort: str = "new"
    ) -> List[dict]:
        query = db.query(models.Post)
        
        if sort == "popular":
            query = query.outerjoin(models.Reaction).group_by(models.Post.id).order_by(
                desc(func.count(models.Reaction.id))
            )
        else:
            query = query.order_by(desc(models.Post.created_at))
        
        posts = query.offset(skip * limit).limit(limit).all()
        
        result = []
        for post in posts:
            like_count = db.query(models.Reaction).filter(
                models.Reaction.post_id == post.id,
                models.Reaction.reaction_type == "like"
            ).count()
            
            dislike_count = db.query(models.Reaction).filter(
                models.Reaction.post_id == post.id,
                models.Reaction.reaction_type == "dislike"
            ).count()
            
            post_dict = {
                "id": post.id,
                "title": post.title,
                "description": post.description,
                "image_url": post.image_url,
                "user_id": post.user_id,
                "created_at": post.created_at,
                "user": post.user,
                "like_count": like_count,
                "dislike_count": dislike_count
            }
            result.append(post_dict)
        
        return result