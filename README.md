# CineBrain - Movie Recommendations with SurrealDB

CineBrain is a web application that analyzes user preferences (ratings, genres, directors) and recommends movies similar to those they've already liked. The system is based on SurrealDB, a modern hybrid database (graph + document) that allows connecting users, movies, and genres in a relational structure without a rigid schema.

## Features

- User registration and authentication (JWT-based)
- Browse movies and submit ratings
- Intelligent recommendations based on:
  - Similar movies (same genres as rated movies)
  - Similar users (movies liked by users with similar preferences)
- Modern React frontend with responsive design
- RESTful API built with FastAPI
- Docker-based deployment

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Database | SurrealDB (hybrid graph + document) |
| Backend | Python (FastAPI) |
| Frontend | React (Vite) |
| Deployment | Docker + Docker Compose |

## Project Structure

```
cinebrain/
├── backend/              # FastAPI backend
│   ├── app.py            # Main application
│   ├── surreal_client.py # SurrealDB client
│   ├── queries/          # SurrealQL query files
│   └── requirements.txt  # Python dependencies
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── api/          # API client
│   └── package.json      # Node dependencies
├── db/                   # Database initialization
│   ├── init.surql        # Basic initialization (legacy)
│   ├── fixtures.surql    # Comprehensive fixture data
│   └── README.md         # Fixture documentation
├── docs/                 # Documentation
│   ├── project_overview.md
│   └── comparison.md
└── docker-compose.yml    # Docker orchestration
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CineBrain
```

2. Start all services:
```bash
docker-compose up
```

This will start:
- SurrealDB on `http://localhost:8000`
- Backend API on `http://localhost:8001`
- Frontend on `http://localhost:3000`

3. Access the application:
- Frontend: http://localhost:3000
- SurrealDB Web UI: http://localhost:8000 (login: root/root)
- API Docs: http://localhost:8001/docs

### First Steps

1. Register a new account or login
2. Browse movies and rate them (1-10 scale)
3. View personalized recommendations based on your ratings

## Database Schema

### Tables

- `user`: User information (name, email, age)
- `movie`: Movie information (title, year, director)
- `genre`: Genre categories
- `rating`: Relationship between users and movies

### Relationships

- `user->rated->movie`: User rates a movie with a score
- `movie->belongs_to->genre`: Movie belongs to one or more genres

### Example Data (Fixtures)

The database is automatically loaded with comprehensive fixtures on first startup, including:
- **8 users** (Oskar, Anna, John, Maria, Sarah, Mike, Lisa, Tom)
- **20 movies** across various genres and years
- **8 genres** (Sci-Fi, Thriller, Drama, Action, Crime, Horror, Comedy, Adventure)
- **50+ ratings** with diverse user preferences
- **40+ genre relationships** connecting movies to genres

The fixtures are automatically loaded when the backend starts if the database is empty. You can also manually reload fixtures using the API endpoint:

```bash
POST /api/fixtures/load
```

Or run the fixture loader script directly:

```bash
cd backend
python load_fixtures.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Movies
- `GET /api/movies` - List all movies
- `GET /api/movies/{movie_id}` - Get movie details
- `GET /api/movies/{movie_id}/genres` - Get movie genres

### Ratings
- `POST /api/ratings` - Submit a rating (requires auth)
- `GET /api/users/{user_id}/ratings` - Get user's ratings

### Recommendations
- `GET /api/recommendations/similar-movies` - Get movie recommendations (requires auth)
- `GET /api/recommendations/similar-users?movie_id={id}` - Get movies liked by similar users

### Fixtures
- `POST /api/fixtures/load` - Reload database fixtures (useful for resetting demo data)

## Example Queries

### Movies liked by a user
```sql
SELECT ->rated->movie->title FROM user:oskar;
```

### Movies in same genre as user's rated movies
```sql
SELECT ->rated->movie->belongs_to-><-belongs_to<-movie
FROM user:oskar
FETCH ->rated->movie->belongs_to;
```

### Users with similar preferences
```sql
SELECT <-rated<-user->rated->movie
FROM movie:inception
FETCH <-rated<-user->rated->movie;
```

## Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8001
```

Set environment variables:
- `SURREAL_URL`: SurrealDB URL (default: http://localhost:8000)
- `SURREAL_USER`: SurrealDB user (default: root)
- `SURREAL_PASS`: SurrealDB password (default: root)
- `JWT_SECRET`: Secret key for JWT tokens

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

Set environment variable:
- `VITE_API_URL`: Backend API URL (default: http://localhost:8001)

### Database Access

#### Option 1: Surrealist (Recommended Visual IDE)
SurrealDB redirects to [Surrealist](https://surrealdb.com/surrealist), the official visual IDE for SurrealDB.

1. **Launch Surrealist in browser**: Visit https://surrealdb.com/surrealist
2. **Or download desktop app**: Available for Windows, macOS, and Linux
3. **Connect to your database**:
   - **Connection Type**: Select "Connection" (not "Local")
   - **Protocol**: `HTTP` or `ws` (WebSocket)
   - **Endpoint/URL**: `http://localhost:8000` or `ws://localhost:8000`
   - **Authentication Method**: Select "Root" or "Database" (not Basic Auth)
   - **Username**: `root`
   - **Password**: `root`
   - **Namespace**: `test`
   - **Database**: `test`

**Note**: If "Basic Auth" is not available, use "Root" authentication method instead. SurrealDB uses root-level authentication, not HTTP Basic Auth.

Once connected, you can:
- Browse tables visually
- Run queries in the query editor
- Explore relationships in the graph view
- Edit data directly

#### Option 2: Direct API Access (curl)
You can query directly via HTTP API using raw SQL:

```bash
# Query movies
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  --data-raw "USE NS test DB test; SELECT * FROM movie;"

# Query users
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  --data-raw "USE NS test DB test; SELECT * FROM user;"

# Check database info
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  --data-raw "USE NS test DB test; INFO FOR DB;"
```

#### Option 3: Use Example Queries
See `db/example_queries.surql` for ready-to-use queries you can run in Surrealist.

#### Via API
```bash
curl -X POST http://localhost:8000/sql \
  -H "Authorization: Basic $(echo -n 'root:root' | base64)" \
  -H "NS: test" \
  -H "DB: test" \
  -H "Content-Type: text/plain" \
  -d "USE NS test DB test; SELECT * FROM movie;"
```

## Why SurrealDB?

SurrealDB combines the best of both worlds:
- **Document Database**: Store flexible JSON data
- **Graph Database**: Native relationship support with RELATE
- **SQL-like Queries**: Familiar syntax with graph capabilities
- **Schemaless**: No migrations needed for schema changes

This makes it ideal for recommendation systems that need:
- Flexible data models
- Complex relationship queries
- Fast iteration and prototyping

## Documentation

- [Project Overview](docs/project_overview.md) - Detailed explanation of the problem and solution
- [SurrealDB vs MongoDB vs Neo4j Comparison](docs/comparison.md) - Comparison with document and graph databases

## Project Goals

- Demonstrate hybrid data modeling with SurrealDB
- Show flexible relationships without schema migrations
- Compare query efficiency: SurrealDB vs MongoDB vs Neo4j
- Provide a complete, runnable example in Docker

## License

This project is created for educational purposes as a demonstration of SurrealDB capabilities in building recommendation systems.

## Contributing

This is an educational project. Feel free to fork and experiment!

## Acknowledgments

- SurrealDB for the innovative hybrid database
- FastAPI for the excellent Python web framework
- React for the frontend framework
