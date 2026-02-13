# SurrealDB Query Examples with cURL

This document contains useful cURL commands to query the CineBrain SurrealDB database.

## Connection Details

- **URL**: `http://localhost:8000`
- **Authentication**: Basic Auth (root:root)
- **Namespace**: `test`
- **Database**: `test`

## Basic Query Format

```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; YOUR_QUERY_HERE;"
```

## Users

### Get All Users
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM user;"
```

### Get Specific User
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM user:oskar;"
```

### Get User by Email
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM user WHERE email = 'oskar@example.com';"
```

## Movies

### Get All Movies
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM movie ORDER BY year DESC;"
```

### Get Featured Movies Only
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM movie WHERE featured = true ORDER BY year DESC;"
```

### Get Non-Featured Movies (Recommendation Only)
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM movie WHERE featured = false ORDER BY year DESC;"
```

### Get Specific Movie
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM movie:inception;"
```

### Get Movies by Director
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM movie WHERE director = 'Christopher Nolan';"
```

## Ratings

### Get All Ratings
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM rated;"
```

### Get All Ratings with User and Movie Details
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT in AS user_id, out AS movie_id, score, created_at FROM rated FETCH in, out;"
```

### Get Ratings for Specific User
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM rated WHERE in = 'user:oskar';"
```

### Get User's Ratings with Movie Details
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT ->rated->movie AS movie, ->rated.score AS score, ->rated.created_at AS created_at FROM user:oskar FETCH ->rated;"
```

### Get Ratings for Specific Movie
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM rated WHERE out = 'movie:inception';"
```

### Get Average Rating per Movie
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT movie.title, math::mean(<-rated<-rated.score) AS avg_rating FROM movie GROUP BY movie.title;"
```

### Get All Scores of Users (Detailed View)
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT <-rated<-user.name AS user_name, <-rated<-user.email AS user_email, ->rated->movie.title AS movie_title, score, created_at FROM rated FETCH in, out;"
```

## Genres

### Get All Genres
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT * FROM genre;"
```

### Get Movies in a Specific Genre
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT <-belongs_to<-movie FROM genre:sci_fi FETCH <-belongs_to<-movie;"
```

### Get Genres for a Specific Movie
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT ->belongs_to->genre FROM movie:inception FETCH ->belongs_to;"
```

## Recommendations

### Get Movies in Same Genres as User's Rated Movies
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT ->rated->movie->belongs_to->genre FROM user:oskar FETCH ->rated->movie->belongs_to;"
```

### Get Movies Rated by Users Who Also Rated a Specific Movie
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT <-rated<-user->rated->movie FROM movie:inception FETCH <-rated<-user->rated->movie;"
```

## Statistics

### Count Movies per Genre
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT genre.name, count(<-belongs_to<-movie) AS movie_count FROM genre GROUP BY genre.name;"
```

### Count Ratings per User
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT user.name, count(->rated->movie) AS rating_count FROM user GROUP BY user.name;"
```

### Get User's Favorite Genres (Based on Ratings)
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT genre.name, count(->rated->movie->belongs_to->genre) AS preference_count FROM user:oskar GROUP BY genre.name;"
```

### Get Top Rated Movies
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT movie.title, math::mean(<-rated<-rated.score) AS avg_rating, count(<-rated<-rated) AS rating_count FROM movie GROUP BY movie.title ORDER BY avg_rating DESC;"
```

## Advanced Queries

### Get All Data for a User (Ratings, Movies, Genres)
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT ->rated->movie->belongs_to->genre FROM user:oskar FETCH ->rated->movie->belongs_to;"
```

### Find Movies with Highest Average Rating
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT movie.title, math::mean(<-rated<-rated.score) AS avg_rating FROM movie WHERE count(<-rated<-rated) > 0 GROUP BY movie.title ORDER BY avg_rating DESC LIMIT 10;"
```

### Find Most Active Users (Most Ratings)
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT user.name, count(->rated->movie) AS total_ratings FROM user GROUP BY user.name ORDER BY total_ratings DESC;"
```

### Get Recent Ratings
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT in AS user_id, out AS movie_id, score, created_at FROM rated ORDER BY created_at DESC LIMIT 20;"
```

## Database Info

### Get Database Information
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; INFO FOR DB;"
```

### Count All Records
```bash
curl -X POST http://localhost:8000/sql \
  -u root:root \
  -H "NS: test" \
  -H "DB: test" \
  -H "Accept: application/json" \
  -H "Content-Type: text/plain" \
  --data-raw "USE NS test DB test; SELECT count() FROM user; SELECT count() FROM movie; SELECT count() FROM rated; SELECT count() FROM genre;"
```
