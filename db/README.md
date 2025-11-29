# Database Fixtures

This directory contains database initialization and fixture files for CineBrain.

## Files

- `init.surql` - Basic initialization script (legacy, kept for reference)
- `fixtures.surql` - Comprehensive fixture data with users, movies, genres, and relationships

## Fixture Contents

The `fixtures.surql` file includes:

### Users (8)
- Oskar, Anna, John, Maria, Sarah, Mike, Lisa, Tom
- All users have password: `password123` (for demo purposes)

### Movies (20)
Popular movies across different genres:
- Sci-Fi: Inception, The Matrix, Interstellar, Blade Runner 2049, Arrival, Dune
- Crime/Drama: The Godfather, Goodfellas, The Departed, Pulp Fiction, Se7en, Zodiac
- Action: The Dark Knight, Kill Bill, Inglourious Basterds
- Drama: Parasite, Joker, Fight Club, The Shawshank Redemption, Forrest Gump

### Genres (8)
- Sci-Fi, Thriller, Drama, Action, Crime, Horror, Comedy, Adventure

### Relationships
- 50+ user ratings (scores 1-10)
- 40+ movie-genre relationships

## Loading Fixtures

### Automatic Loading
Fixtures are automatically loaded when the backend starts if the database is empty.

### Manual Loading

#### Via API
```bash
curl -X POST http://localhost:8001/api/fixtures/load
```

#### Via Python Script
```bash
cd backend
python load_fixtures.py
```

#### Via SurrealDB Web UI
1. Access http://localhost:8000
2. Copy and paste the contents of `fixtures.surql`
3. Execute the queries

## Customizing Fixtures

To add your own data:
1. Edit `fixtures.surql`
2. Add your CREATE and RELATE statements
3. Reload fixtures using one of the methods above

## Notes

- Fixtures use `CREATE TABLE IF NOT EXISTS` to avoid errors on reload
- All timestamps use `time::now()` for current time
- User passwords are stored in plain text for demo purposes (not recommended for production)

