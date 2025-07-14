from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db import models, schemas
from ..core.security import get_current_user

router = APIRouter()

@router.post("/posts/{post_id}/reaction", response_model=schemas.Reaction)
def create_or_update_reaction(
    post_id: int,
    reaction: schemas.ReactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_reaction = db.query(models.Reaction).filter(
        models.Reaction.user_id == current_user.id,
        models.Reaction.post_id == post_id
    ).first()
    
    if existing_reaction:
        existing_reaction.reaction_type = reaction.reaction_type
        db.commit()
        db.refresh(existing_reaction)
        return existing_reaction
    else:
        db_reaction = models.Reaction(
            user_id=current_user.id,
            post_id=post_id,
            reaction_type=reaction.reaction_type
        )
        db.add(db_reaction)
        db.commit()
        db.refresh(db_reaction)
        return db_reaction

@router.get("/posts/{post_id}/reactions", response_model=schemas.ReactionSummary)
def get_post_reactions(post_id: int, db: Session = Depends(get_db)):
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
    
    return schemas.ReactionSummary(
        like_count=like_count,
        dislike_count=dislike_count
    )

@router.delete("/posts/{post_id}/reaction")
def delete_reaction(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    reaction = db.query(models.Reaction).filter(
        models.Reaction.user_id == current_user.id,
        models.Reaction.post_id == post_id
    ).first()
    
    if reaction is None:
        raise HTTPException(status_code=404, detail="Reaction not found")
    
    db.delete(reaction)
    db.commit()
    return {"message": "Reaction removed successfully"}