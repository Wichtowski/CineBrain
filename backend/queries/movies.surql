SELECT * FROM movie ORDER BY year DESC;

SELECT * FROM movie WHERE id = $movie_id;

SELECT ->rated->movie FROM user WHERE id = $user_id;

SELECT ->belongs_to->genre FROM movie WHERE id = $movie_id;

