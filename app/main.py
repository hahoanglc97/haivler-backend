from fastapi import FastAPI, Depends, HTTPException, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from .api import auth, users, posts, comments, reactions
from .core.config import settings
from .core.middleware import URLObfuscationMiddleware, URLMappingResponse
from .core.security import get_current_user
from .db.database import engine, get_db
from .db import models, schemas
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add URL obfuscation middleware
url_obfuscation_middleware = URLObfuscationMiddleware(app, settings.SECRET_KEY)
app.add_middleware(URLObfuscationMiddleware, secret_key=settings.SECRET_KEY)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(posts.router, prefix=f"{settings.API_V1_STR}/posts", tags=["posts"])
app.include_router(comments.router, prefix=f"{settings.API_V1_STR}", tags=["comments"])
app.include_router(reactions.router, prefix=f"{settings.API_V1_STR}", tags=["reactions"])

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/system/endpoints")
def get_obfuscated_endpoints(current_user: models.User = Depends(get_current_user)):
    """Get obfuscated endpoint URLs for authenticated users"""
    url_mapper = URLMappingResponse(url_obfuscation_middleware)
    return {
        "message": "Obfuscated endpoint mappings",
        "endpoints": url_mapper.get_endpoints(),
        "usage_notes": {
            "security_headers": "Include X-Timestamp and X-Access-Token for enhanced security",
            "token_validity": "Access tokens are valid for 5 minutes",
            "direct_access": "Direct API calls to /api/v1/* will be redirected or blocked"
        }
    }

@app.get("/api/v1/system/token/{endpoint_hash}")
def generate_access_token(endpoint_hash: str, current_user: models.User = Depends(get_current_user)):
    """Generate fresh access token for a specific obfuscated endpoint"""
    obfuscated_path = f"/api/x/{endpoint_hash}"
    
    # Verify the endpoint exists
    if obfuscated_path not in url_obfuscation_middleware.reverse_mapping:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    token_info = url_obfuscation_middleware.generate_access_token(obfuscated_path)
    return {
        "endpoint": obfuscated_path,
        "access_token": token_info,
        "headers": {
            "X-Timestamp": token_info["timestamp"],
            "X-Access-Token": token_info["token"]
        }
    }

# Create dynamic routes for obfuscated endpoints
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/api/x/1f217a698b25")  # Register endpoint
def obfuscated_register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return auth.register(user, db)

@app.post("/api/x/9592fc5373e2")  # Login endpoint  
def obfuscated_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return auth.login(form_data, db)

@app.get("/api/x/5baaf1c55a0a")  # Users/me endpoint
def obfuscated_users_me(current_user: models.User = Depends(get_current_user)):
    return users.read_users_me(current_user)

@app.put("/api/x/5baaf1c55a0a")  # Users/me update endpoint
def obfuscated_users_update(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return users.update_user_me(user_update, db, current_user)

@app.get("/api/x/ff0d498c575b")  # Posts endpoint
def obfuscated_posts_list(
    skip: int = 0,
    limit: int = 10,
    sort: str = "new",
    db: Session = Depends(get_db)
):
    return posts.read_posts(skip, limit, sort, db)

@app.post("/api/x/ff0d498c575b")  # Posts create endpoint
def obfuscated_posts_create(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return posts.create_post(title, description, image, db, current_user)

@app.get("/api/x/ff0d498c575b/{post_id}")  # Get single post
def obfuscated_get_post(post_id: int, db: Session = Depends(get_db)):
    return posts.read_post(post_id, db)

@app.put("/api/x/ff0d498c575b/{post_id}")  # Update post
def obfuscated_update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return posts.update_post(post_id, post_update, db, current_user)

@app.delete("/api/x/ff0d498c575b/{post_id}")  # Delete post
def obfuscated_delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return posts.delete_post(post_id, db, current_user)

# Comments endpoints
@app.get("/api/x/ff0d498c575b/{post_id}/comments")  # Get comments
def obfuscated_get_comments(post_id: int, db: Session = Depends(get_db)):
    return comments.read_comments(post_id, db)

@app.post("/api/x/ff0d498c575b/{post_id}/comments")  # Create comment
def obfuscated_create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return comments.create_comment(post_id, comment, db, current_user)

@app.delete("/api/x/0ebcf2cda524/{comment_id}")  # Delete comment
def obfuscated_delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return comments.delete_comment(comment_id, db, current_user)

# Reactions endpoints
@app.get("/api/x/ff0d498c575b/{post_id}/reactions")  # Get reactions
def obfuscated_get_reactions(post_id: int, db: Session = Depends(get_db)):
    return reactions.get_post_reactions(post_id, db)

@app.post("/api/x/ff0d498c575b/{post_id}/reaction")  # Create reaction
def obfuscated_create_reaction(
    post_id: int,
    reaction: schemas.ReactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return reactions.create_or_update_reaction(post_id, reaction, db, current_user)

@app.delete("/api/x/ff0d498c575b/{post_id}/reaction")  # Delete reaction
def obfuscated_delete_reaction(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return reactions.delete_reaction(post_id, db, current_user)