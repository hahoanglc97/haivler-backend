from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from ..db.database import get_db
from ..db import models, schemas
from ..core.security import get_current_user
from ..utils.minio_client import minio_client

router = APIRouter()

@router.get("/", response_model=List[schemas.Post])
def read_posts(
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort: str = Query("new", regex="^(new|popular)$"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Post)
    
    if sort == "popular":
        query = query.outerjoin(models.Reaction).group_by(models.Post.id).order_by(
            desc(func.count(models.Reaction.id))
        )
    else:
        query = query.order_by(desc(models.Post.created_at))
    
    posts = query.offset(skip * limit).limit(limit).all()
    return posts

@router.get("/{post_id}", response_model=schemas.PostWithDetails)
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    like_count = db.query(models.Reaction).filter(
        models.Reaction.post_id == post_id,
        models.Reaction.reaction_type == "like"
    ).count()
    
    dislike_count = db.query(models.Reaction).filter(
        models.Reaction.post_id == post_id,
        models.Reaction.reaction_type == "dislike"
    ).count()
    
    post_dict = post.__dict__.copy()
    post_dict["like_count"] = like_count
    post_dict["dislike_count"] = dislike_count
    
    return post_dict

@router.post("/", response_model=schemas.Post)
def create_post(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    image_url = minio_client.upload_file(image)
    
    db_post = models.Post(
        title=title,
        description=description,
        image_url=image_url,
        user_id=current_user.id
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.put("/{post_id}", response_model=schemas.Post)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if post_update.title is not None:
        post.title = post_update.title
    if post_update.description is not None:
        post.description = post_update.description
    
    db.commit()
    db.refresh(post)
    return post

@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    minio_client.delete_file(post.image_url)
    
    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}