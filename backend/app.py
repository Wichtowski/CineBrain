from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from jose import jwt
from datetime import datetime, timedelta
from surreal_client import SurrealClient
from pathlib import Path
import os
import traceback

app = FastAPI(title="CineBrain API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception: {exc}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Credentials": "true",
        }
    )

SURREAL_URL = os.getenv("SURREAL_URL", "http://127.0.0.1:8000")
SURREAL_USER = os.getenv("SURREAL_USER", "root")
SURREAL_PASS = os.getenv("SURREAL_PASS", "root")
SURREAL_NS = os.getenv("SURREAL_NS", "test")
SURREAL_DB = os.getenv("SURREAL_DB", "test")
JWT_SECRET = os.getenv("JWT_SECRET", "secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

surreal_client = SurrealClient(
    url=SURREAL_URL,
    user=SURREAL_USER,
    password=SURREAL_PASS,
    namespace=SURREAL_NS,
    database=SURREAL_DB
)

async def load_fixtures() -> None:
    # Try multiple possible paths for the fixtures file
    possible_paths = [
        Path("/db/fixtures.surql"),  # Docker volume mount
        Path(__file__).parent.parent / "db" / "fixtures.surql",  # Relative from backend
        Path(__file__).parent / ".." / "db" / "fixtures.surql",  # Alternative relative
    ]
    
    fixtures_path = None
    for path in possible_paths:
        if path.exists():
            fixtures_path = path
            break
    
    if not fixtures_path or not fixtures_path.exists():
        print(f"Fixtures file not found. Tried paths: {[str(p) for p in possible_paths]}")
        return
    
    print(f"Loading fixtures from: {fixtures_path}")
    
    try:
        with open(fixtures_path, "r", encoding="utf-8") as f:
            fixtures_sql = f.read()
        
        queries = [q.strip() for q in fixtures_sql.split(";") if q.strip() and not q.strip().upper().startswith("USE")]
        
        print(f"Loading {len(queries)} fixture statements (skipping USE statements)...")
        
        success_count = 0
        error_count = 0
        
        for i, query in enumerate(queries, 1):
            if query:
                try:
                    await surreal_client.query(query + ";")
                    success_count += 1
                    if i % 20 == 0 or i <= 5:
                        print(f"Processed {i}/{len(queries)} statements... ({success_count} successful, {error_count} errors)")
                except Exception as e:
                    error_count += 1
                    error_msg = str(e)
                    if "already exists" not in error_msg.lower() and "duplicate" not in error_msg.lower():
                        print(f"Error executing query {i}: {e}")
                        print(f"Query: {query[:200]}...")
        
        print(f"Fixtures loading complete! {success_count} successful, {error_count} errors out of {len(queries)} total queries.")
        
        if error_count > 0:
            print(f"Note: {error_count} queries had errors (some may be expected, like 'already exists' errors).")
    except Exception as e:
        print(f"Error loading fixtures: {e}")
        import traceback
        print(traceback.format_exc())

@app.on_event("startup")
async def startup():
    import asyncio
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to SurrealDB (attempt {attempt + 1}/{max_retries})...")
            await surreal_client.connect()
            print("Successfully connected to SurrealDB!")
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Connection failed: {e}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print(f"Failed to connect to SurrealDB after {max_retries} attempts: {e}")
                raise
    
    try:
        users_result = await surreal_client.query("SELECT * FROM user LIMIT 1;")
        movies_result = await surreal_client.query("SELECT * FROM movie LIMIT 1;")
        
        def has_data(result):
            if not result:
                return False
            if isinstance(result, list):
                return len([r for r in result if r is not None and (not isinstance(r, dict) or "id" in r or "result" in r)]) > 0
            return True
        
        users_has_data = has_data(users_result)
        movies_has_data = has_data(movies_result)
        
        if not users_has_data or not movies_has_data:
            print("Database appears empty, loading fixtures...")
            print(f"Users check: {users_result} (has data: {users_has_data})")
            print(f"Movies check: {movies_result} (has data: {movies_has_data})")
            await load_fixtures()
            
            users_after = await surreal_client.query("SELECT * FROM user LIMIT 1;")
            movies_after = await surreal_client.query("SELECT * FROM movie LIMIT 1;")
            
            if has_data(users_after) and has_data(movies_after):
                print("Fixtures loaded successfully!")
            else:
                print("Warning: Fixtures may not have loaded correctly.")
                print(f"Users after: {users_after}, Movies after: {movies_after}")
        else:
            print("Database already contains data, skipping fixture load.")
    except Exception as e:
        print(f"Warning: Could not check database state: {e}")
        import traceback
        print(traceback.format_exc())
        print("Attempting to load fixtures anyway...")
        try:
            await load_fixtures()
        except Exception as fixture_error:
            print(f"Failed to load fixtures: {fixture_error}")
            import traceback
            print(traceback.format_exc())

@app.on_event("shutdown")
async def shutdown():
    await surreal_client.close()

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = None
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RatingCreate(BaseModel):
    movie_id: str
    score: int

class MovieResponse(BaseModel):
    id: str
    title: str
    year: Optional[int] = None
    director: Optional[str] = None

class RatingResponse(BaseModel):
    id: str
    in_node: str = Field(alias="in")
    out: str
    score: int
    created_at: Optional[str] = None
    
    class Config:
        populate_by_name = True

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def create_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

@app.post("/api/auth/register")
async def register(user_data: UserCreate) -> Dict[str, Any]:
    existing_users = await surreal_client.query(
        f"SELECT * FROM user WHERE email = '{user_data.email}';"
    )
    if existing_users:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user_id = user_data.email.split("@")[0].lower().replace(".", "_")
    user = await surreal_client.create(
        "user",
        {
            "name": user_data.name,
            "email": user_data.email,
            "age": user_data.age
        },
        user_id
    )
    
    token = create_token(f"user:{user_id}", user_data.email)
    return {"token": token, "user": user}

@app.post("/api/auth/login")
async def login(credentials: UserLogin) -> Dict[str, Any]:
    try:
        if credentials.password != "password123":
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        users = await surreal_client.query(
            f"SELECT * FROM user WHERE email = '{credentials.email}';"
        )
        if not users:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = users[0]
        
        if not isinstance(user, dict):
            if isinstance(user, str):
                user_id = user.replace("user:", "").split(":")[0] if ":" in user else user
            else:
                raise HTTPException(status_code=500, detail=f"Unexpected user data format: {type(user)}")
        else:
            user_id = user.get("id", "")
            if isinstance(user_id, str) and ":" in user_id:
                user_id = user_id.split(":")[-1]
            else:
                user_id = str(user_id)
        
        token = create_token(f"user:{user_id}", credentials.email)
        
        if isinstance(user, dict):
            user_response = {k: v for k, v in user.items() if k != "password"}
        else:
            user_response = {"id": f"user:{user_id}", "email": credentials.email}
        
        return {"token": token, "user": user_response}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/api/movies")
async def get_movies(all: bool = False) -> List[Dict[str, Any]]:
    try:
        if all:
            movies = await surreal_client.query("SELECT * FROM movie ORDER BY year DESC;")
        else:
            movies = await surreal_client.query("SELECT * FROM movie WHERE featured = true OR featured IS NONE ORDER BY year DESC;")
        if not isinstance(movies, list):
            return []
        filtered = [m for m in movies if isinstance(m, dict) and m.get("id") and (not isinstance(m.get("id"), str) or (isinstance(m.get("id"), str) and not m.get("id").startswith("Specify")))]
        return filtered
    except Exception as e:
        print(f"Error fetching movies: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error fetching movies: {str(e)}")

@app.get("/api/movies/{movie_id}/genres")
async def get_movie_genres(movie_id: str) -> List[Dict[str, Any]]:
    genres = await surreal_client.query(
        f"SELECT ->belongs_to->genre FROM movie WHERE id = 'movie:{movie_id}';"
    )
    return genres

@app.post("/api/ratings")
async def create_rating(rating: RatingCreate, current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    user_id = current_user["id"]
    user_id_clean = user_id.split(":")[-1] if ":" in user_id else user_id
    movie_id_clean = rating.movie_id
    
    existing_ratings = await surreal_client.query(
        f"SELECT id FROM rated WHERE in = 'user:{user_id_clean}' AND out = 'movie:{movie_id_clean}';"
    )
    
    if existing_ratings and isinstance(existing_ratings, list) and len(existing_ratings) > 0:
        for existing in existing_ratings:
            if isinstance(existing, dict):
                rating_id = existing.get("id", "")
                if rating_id:
                    await surreal_client.query(
                        f"DELETE {rating_id};"
                    )
    
    result = await surreal_client.relate(
        "user",
        user_id_clean,
        "rated",
        "movie",
        movie_id_clean,
        {"score": rating.score, "created_at": datetime.utcnow().isoformat()}
    )
    return result

@app.get("/api/users/{user_id}/ratings")
async def get_user_ratings(user_id: str) -> List[Dict[str, Any]]:
    ratings = await surreal_client.query(
        f"SELECT ->rated->movie FROM user WHERE id = 'user:{user_id}';"
    )
    return ratings

@app.get("/api/auth/me")
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    user_id = current_user["id"]
    user_id_clean = user_id.split(":")[-1] if ":" in user_id else user_id
    
    users = await surreal_client.query(
        f"SELECT * FROM user WHERE id = 'user:{user_id_clean}';"
    )
    
    if users and len(users) > 0:
        user = users[0]
        if isinstance(user, dict):
            return {k: v for k, v in user.items() if k != "password"}
    
    return {"id": user_id, "email": current_user.get("email", "")}

# @app.get("/api/movies")
# async def get_movies(all: bool = False) -> List[Dict[str, Any]]:
#     try:
#         if all:
#             movies = await surreal_client.query("SELECT * FROM movie ORDER BY year DESC;")
#         else:
#             movies = await surreal_client.query("SELECT * FROM movie WHERE featured = true OR featured IS NONE ORDER BY year DESC;")
#         if not isinstance(movies, list):
#             return []
#         filtered = [m for m in movies if isinstance(m, dict) and m.get("id") and (not isinstance(m.get("id"), str) or (isinstance(m.get("id"), str) and not m.get("id").startswith("Specify")))]
#         return filtered
#     except Exception as e:
#         print(f"Error fetching movies: {e}")
#         import traceback
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Error fetching movies: {str(e)}")

@app.get("/api/ratings/my-ratings")
async def get_my_ratings(current_user: Dict[str, Any] = Depends(get_current_user)) -> List[Dict[str, Any]]:
    user_id = current_user["id"]
    user_id_clean = user_id.split(":")[-1] if ":" in user_id else user_id
    
    ratings = await surreal_client.query(
        f"SELECT ->rated->movie AS movie, ->rated.score AS score, ->rated.created_at AS created_at FROM user:{user_id_clean} FETCH ->rated->movie;"
    )
    
    result = []
    movie_ratings = {}
    
    if ratings and isinstance(ratings, list):
        for item in ratings:
            if isinstance(item, dict):
                movies = item.get("movie", [])
                scores = item.get("score", [])
                created_ats = item.get("created_at", [])
                
                if isinstance(movies, list) and isinstance(scores, list):
                    for i, movie in enumerate(movies):
                        if i < len(scores):
                            movie_data = movie if isinstance(movie, dict) else {}
                            movie_id = movie_data.get("id", "") if isinstance(movie, dict) else (movie if isinstance(movie, str) else "")
                            score = scores[i] if i < len(scores) else None
                            created_at = created_ats[i] if i < len(created_ats) else None
                            
                            if movie_id:
                                if movie_id not in movie_ratings:
                                    movie_ratings[movie_id] = {
                                        "movie_id": movie_id,
                                        "score": score,
                                        "created_at": created_at,
                                        "movie": movie_data if isinstance(movie, dict) else None
                                    }
                                else:
                                    existing_date = movie_ratings[movie_id]["created_at"]
                                    if created_at and existing_date:
                                        if created_at > existing_date:
                                            movie_ratings[movie_id] = {
                                                "movie_id": movie_id,
                                                "score": score,
                                                "created_at": created_at,
                                                "movie": movie_data if isinstance(movie, dict) else None
                                            }
    
    result = list(movie_ratings.values())
    return result

@app.get("/api/recommendations/similar-movies")
async def get_similar_movies(current_user: Dict[str, Any] = Depends(get_current_user)) -> List[Dict[str, Any]]:
    try:
        user_id_raw = current_user["id"]
        if isinstance(user_id_raw, str):
            if ":" in user_id_raw:
                user_id = user_id_raw.split(":")[-1]
            else:
                user_id = user_id_raw
        else:
            user_id = str(user_id_raw)
        
        if not user_id or user_id == "Specify a namespace to use" or len(user_id) > 50:
            return []
        
        user_ratings_query = await surreal_client.query(
            f"SELECT ->rated->movie AS movie FROM user:{user_id} FETCH ->rated;"
        )
        
        rated_movie_ids = set()
        if user_ratings_query and isinstance(user_ratings_query, list):
            for item in user_ratings_query:
                if isinstance(item, dict):
                    movies = item.get("movie", [])
                    if isinstance(movies, list):
                        for movie in movies:
                            movie_id = movie if isinstance(movie, str) else (movie.get("id", "") if isinstance(movie, dict) else "")
                            if movie_id:
                                rated_movie_ids.add(movie_id)
        
        if not rated_movie_ids:
            return []
        
        rated_movies_data = await surreal_client.query(
            f"SELECT ->rated->movie AS movie FROM user:{user_id} FETCH ->rated->movie;"
        )
        
        genre_ids = set()
        directors = set()
        rated_movies_full = []
        
        if rated_movies_data and isinstance(rated_movies_data, list):
            for item in rated_movies_data:
                if isinstance(item, dict):
                    movies = item.get("movie", [])
                    if isinstance(movies, list):
                        for movie in movies:
                            if isinstance(movie, dict):
                                rated_movies_full.append(movie)
                                # Get director
                                if "director" in movie and movie["director"]:
                                    directors.add(movie["director"])
                            elif isinstance(movie, str) and movie.startswith("movie:"):
                                movie_clean = movie.split(":")[-1] if ":" in movie else movie
                                movie_obj = await surreal_client.query(f"SELECT * FROM movie:{movie_clean};")
                                if movie_obj and isinstance(movie_obj, list) and len(movie_obj) > 0:
                                    movie_data = movie_obj[0]
                                    if isinstance(movie_data, dict):
                                        rated_movies_full.append(movie_data)
                                        if "director" in movie_data and movie_data["director"]:
                                            directors.add(movie_data["director"])
        
        # Get genres from rated movies
        user_genres_query = await surreal_client.query(
            f"SELECT ->rated->movie->belongs_to->genre FROM user:{user_id} FETCH ->rated->movie->belongs_to;"
        )
        
        if user_genres_query and isinstance(user_genres_query, list):
            for item in user_genres_query:
                if isinstance(item, dict):
                    rated_key = "->rated"
                    if rated_key in item:
                        rated_data = item[rated_key]
                        if isinstance(rated_data, dict):
                            movie_key = "->movie"
                            if movie_key in rated_data:
                                movie_data = rated_data[movie_key]
                                if isinstance(movie_data, dict):
                                    belongs_to_key = "->belongs_to"
                                    if belongs_to_key in movie_data:
                                        belongs_to = movie_data[belongs_to_key]
                                        if isinstance(belongs_to, dict):
                                            genre_key = "->genre"
                                            if genre_key in belongs_to:
                                                genres = belongs_to[genre_key]
                                                if isinstance(genres, list):
                                                    for genre in genres:
                                                        genre_id = genre if isinstance(genre, str) else (genre.get("id", "") if isinstance(genre, dict) else "")
                                                        if genre_id and genre_id.startswith("genre:"):
                                                            genre_ids.add(genre_id)
        
        print(f"Found {len(genre_ids)} unique genres and {len(directors)} unique directors")
        
        if not genre_ids and not directors:
            print("No genres or directors found, returning empty recommendations")
            return []
        
        recommended_movies_by_id = {}
        recommended_scores_by_id = {}
        rated_movie_ids_set = set(rated_movie_ids)
        print(f"User has rated {len(rated_movie_ids)} movies")
        
        # Get movies by genre
        for genre_id in genre_ids:
            genre_clean = genre_id.split(":")[-1] if ":" in genre_id else genre_id
            print(f"Fetching movies for genre: {genre_clean}")
            movies_in_genre = await surreal_client.query(
                f"SELECT <-belongs_to<-movie FROM genre:{genre_clean} FETCH <-belongs_to<-movie;"
            )
            
            if movies_in_genre and isinstance(movies_in_genre, list):
                for item in movies_in_genre:
                    if isinstance(item, dict):
                        belongs_to_key = "<-belongs_to"
                        if belongs_to_key in item:
                            belongs_to = item[belongs_to_key]
                            if isinstance(belongs_to, dict):
                                movie_key = "<-movie"
                                if movie_key in belongs_to:
                                    movies = belongs_to[movie_key]
                                    if isinstance(movies, list):
                                        for movie in movies:
                                            if isinstance(movie, dict) and "id" in movie:
                                                movie_id = movie["id"]
                                                if movie_id.startswith("movie:") and movie_id not in rated_movie_ids_set:
                                                    recommended_movies_by_id[movie_id] = movie
                                                    recommended_scores_by_id[movie_id] = recommended_scores_by_id.get(movie_id, 0) + 1
                                            elif isinstance(movie, str) and movie.startswith("movie:"):
                                                if movie not in rated_movie_ids_set:
                                                    recommended_scores_by_id[movie] = recommended_scores_by_id.get(movie, 0) + 1
                                                    if movie not in recommended_movies_by_id:
                                                        movie_clean = movie.split(":")[-1] if ":" in movie else movie
                                                        movie_obj = await surreal_client.query(f"SELECT * FROM movie:{movie_clean};")
                                                        if movie_obj and isinstance(movie_obj, list) and len(movie_obj) > 0:
                                                            movie_data = movie_obj[0]
                                                            if isinstance(movie_data, dict) and "id" in movie_data:
                                                                recommended_movies_by_id[movie_data["id"]] = movie_data
        
        # Get movies by director
        for director in directors:
            if director:
                print(f"Fetching movies for director: {director}")
                movies_by_director = await surreal_client.query(
                    f"SELECT * FROM movie WHERE director = '{director}';"
                )
                
                if movies_by_director and isinstance(movies_by_director, list):
                    for movie in movies_by_director:
                        if isinstance(movie, dict) and "id" in movie:
                            movie_id = movie["id"]
                            if movie_id.startswith("movie:") and movie_id not in rated_movie_ids_set:
                                recommended_movies_by_id[movie_id] = movie
                                recommended_scores_by_id[movie_id] = recommended_scores_by_id.get(movie_id, 0) + 1
        
        scored_movies = []
        for movie_id, movie_data in recommended_movies_by_id.items():
            score = recommended_scores_by_id.get(movie_id, 0)
            scored_movies.append((score, movie_id, movie_data))
        
        scored_movies.sort(key=lambda x: (-x[0], x[1]))
        top_movies = [m[2] for m in scored_movies[:10]]
        
        print(f"Returning {len(top_movies)} recommended movies")
        return top_movies
    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        import traceback
        print(traceback.format_exc())
        return []

@app.get("/api/recommendations/similar-users")
async def get_similar_users_movies(movie_id: str) -> List[Dict[str, Any]]:
    query = f"""
    SELECT <-rated<-user->rated->movie AS similar_users_movies
    FROM movie:{movie_id}
    FETCH <-rated<-user->rated->movie;
    """
    result = await surreal_client.query(query)
    if result and isinstance(result, list) and len(result) > 0:
        movies = result[0].get("similar_users_movies", [])
        return movies if isinstance(movies, list) else []
    return []

@app.post("/api/fixtures/load")
async def reload_fixtures() -> Dict[str, str]:
    try:
        await load_fixtures()
        return {"status": "success", "message": "Fixtures loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading fixtures: {str(e)}")

@app.get("/api/graph/data")
async def get_graph_data() -> Dict[str, Any]:
    try:
        users = await surreal_client.query("SELECT id, name, email FROM user;")
        movies = await surreal_client.query("SELECT id, title, year, director FROM movie;")
        ratings = await surreal_client.query("SELECT id, in, out, score FROM rated;")
        
        users_list = []
        if users and isinstance(users, list):
            for user in users:
                if isinstance(user, dict) and user.get("id"):
                    users_list.append({
                        "id": user.get("id", ""),
                        "name": user.get("name", ""),
                        "email": user.get("email", "")
                    })
        
        movies_list = []
        if movies and isinstance(movies, list):
            for movie in movies:
                if isinstance(movie, dict) and movie.get("id"):
                    movies_list.append({
                        "id": movie.get("id", ""),
                        "title": movie.get("title", ""),
                        "year": movie.get("year", None),
                        "director": movie.get("director", "")
                    })
        
        ratings_list = []
        if ratings and isinstance(ratings, list):
            for rating in ratings:
                if isinstance(rating, dict):
                    in_node = rating.get("in", "")
                    out_node = rating.get("out", "")
                    score = rating.get("score", 0)
                    
                    if in_node and out_node and score:
                        ratings_list.append({
                            "id": rating.get("id", ""),
                            "source": in_node,
                            "target": out_node,
                            "score": score
                        })
        
        return {
            "users": users_list,
            "movies": movies_list,
            "ratings": ratings_list
        }
    except Exception as e:
        print(f"Error fetching graph data: {e}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error fetching graph data: {str(e)}")

@app.get("/api/health")
async def health_check() -> Dict[str, str]:
    return {"status": "ok"}

