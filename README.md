# Haivler Backend - Reddit-like Image Sharing API

A FastAPI-based backend for a Reddit-style image sharing application with MySQL database and MinIO object storage.

## Features

- User authentication with JWT tokens
- Image upload and storage with MinIO
- Posts with likes/dislikes (reactions)
- Comments system
- RESTful API design
- Docker containerization
- Database migrations with Alembic

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with username/password
- `POST /api/v1/auth/logout` - Logout

### Users
- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update user profile

### Posts
- `GET /api/v1/posts` - List posts (with pagination and sorting)
- `GET /api/v1/posts/{id}` - Get post details
- `POST /api/v1/posts` - Create new post with image
- `PUT /api/v1/posts/{id}` - Update post (owner only)
- `DELETE /api/v1/posts/{id}` - Delete post (owner only)

### Comments
- `POST /api/v1/posts/{id}/comments` - Add comment to post
- `GET /api/v1/posts/{id}/comments` - Get post comments
- `DELETE /api/v1/comments/{id}` - Delete comment (owner only)

### Reactions
- `POST /api/v1/posts/{id}/reaction` - Like/dislike a post
- `GET /api/v1/posts/{id}/reactions` - Get reaction counts
- `DELETE /api/v1/posts/{id}/reaction` - Remove reaction

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository
2. Navigate to the backend directory
3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
4. Start all services:
   ```bash
   docker-compose up -d
   ```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- MinIO Console: `http://localhost:9001` (admin/admin123)

### Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up MySQL database and MinIO

3. Configure environment variables in `.env`

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

- `SECRET_KEY` - JWT secret key
- `DATABASE_URL` - MySQL connection string
- `MINIO_ENDPOINT` - MinIO server endpoint
- `MINIO_ACCESS_KEY` - MinIO access key
- `MINIO_SECRET_KEY` - MinIO secret key
- `MINIO_BUCKET_NAME` - Bucket for image storage

## Database Models

- **User**: User accounts with authentication
- **Post**: Image posts with metadata
- **Comment**: Comments on posts
- **Reaction**: Like/dislike reactions on posts

## File Upload

Images are uploaded to MinIO object storage with:
- UUID-based filenames
- Content type validation
- Automatic bucket creation
- Public URL generation

## Security

- Password hashing with bcrypt
- JWT token authentication
- CORS configuration
- Input validation with Pydantic
- File type validation for uploads