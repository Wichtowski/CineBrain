-- First, set the namespace and database
USE NS test DB test;

-- View all users
SELECT * FROM user;

-- View all movies
SELECT * FROM movie;

-- View all genres
SELECT * FROM genre;

-- View all ratings (relationships)
SELECT * FROM rated;

-- Get movies rated by a specific user
SELECT ->rated->movie FROM user:oskar;

-- Get genres for a specific movie
SELECT ->belongs_to->genre FROM movie:inception;

-- Get all movies in a specific genre
SELECT <-belongs_to<-movie FROM genre:sci_fi;

-- Get users who rated a specific movie
SELECT <-rated<-user FROM movie:matrix;

-- Get recommendations: movies in same genre as user's rated movies
SELECT ->rated->movie->belongs_to-><-belongs_to<-movie 
FROM user:oskar 
FETCH ->rated->movie->belongs_to;

-- Count movies per genre
SELECT genre.name, count(<-belongs_to<-movie) AS movie_count
FROM genre
GROUP BY genre.name;

-- Get average rating per movie
SELECT movie.title, math::mean(<-rated<-rated.score) AS avg_rating
FROM movie
GROUP BY movie.title;

-- Get user's favorite genres (based on ratings)
SELECT genre.name, count(->rated->movie->belongs_to->genre) AS preference_count
FROM user:oskar
GROUP BY genre.name;

