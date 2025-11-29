SELECT ->rated->movie->belongs_to-><-belongs_to<-movie AS recommended_movies
FROM user WHERE id = $user_id
FETCH ->rated->movie->belongs_to;

SELECT <-rated<-user->rated->movie AS similar_users_movies
FROM movie WHERE id = $movie_id
FETCH <-rated<-user->rated->movie;

SELECT ->rated->movie FROM user WHERE id = $user_id
FETCH ->rated->movie->belongs_to;

SELECT <-rated<-user FROM movie WHERE id = $movie_id
FETCH <-rated<-user->rated->movie;

