CREATE TABLE user;
CREATE TABLE movie;
CREATE TABLE genre;
CREATE TABLE rating;

CREATE user:oskar SET name = "Oskar", age = 26, email = "oskar@example.com";
CREATE user:anna SET name = "Anna", age = 24, email = "anna@example.com";
CREATE user:john SET name = "John", age = 30, email = "john@example.com";
CREATE user:maria SET name = "Maria", age = 28, email = "maria@example.com";

CREATE movie:inception SET title = "Inception", year = 2010, director = "Christopher Nolan";
CREATE movie:matrix SET title = "Matrix", year = 1999, director = "Wachowski Brothers";
CREATE movie:interstellar SET title = "Interstellar", year = 2014, director = "Christopher Nolan";
CREATE movie:blade_runner SET title = "Blade Runner 2049", year = 2017, director = "Denis Villeneuve";
CREATE movie:parasite SET title = "Parasite", year = 2019, director = "Bong Joon-ho";
CREATE movie:joker SET title = "Joker", year = 2019, director = "Todd Phillips";
CREATE movie:fight_club SET title = "Fight Club", year = 1999, director = "David Fincher";
CREATE movie:pulp_fiction SET title = "Pulp Fiction", year = 1994, director = "Quentin Tarantino";

CREATE genre:sci_fi SET name = "Sci-Fi";
CREATE genre:thriller SET name = "Thriller";
CREATE genre:drama SET name = "Drama";
CREATE genre:action SET name = "Action";
CREATE genre:crime SET name = "Crime";

RELATE user:oskar->rated->movie:inception SET score = 9, created_at = time::now();
RELATE user:oskar->rated->movie:matrix SET score = 8, created_at = time::now();
RELATE user:oskar->rated->movie:interstellar SET score = 10, created_at = time::now();
RELATE user:oskar->rated->movie:blade_runner SET score = 9, created_at = time::now();

RELATE user:anna->rated->movie:matrix SET score = 9, created_at = time::now();
RELATE user:anna->rated->movie:parasite SET score = 10, created_at = time::now();
RELATE user:anna->rated->movie:joker SET score = 8, created_at = time::now();

RELATE user:john->rated->movie:inception SET score = 8, created_at = time::now();
RELATE user:john->rated->movie:fight_club SET score = 9, created_at = time::now();
RELATE user:john->rated->movie:pulp_fiction SET score = 10, created_at = time::now();

RELATE user:maria->rated->movie:interstellar SET score = 9, created_at = time::now();
RELATE user:maria->rated->movie:blade_runner SET score = 8, created_at = time::now();
RELATE user:maria->rated->movie:parasite SET score = 9, created_at = time::now();

RELATE movie:inception->belongs_to->genre:sci_fi;
RELATE movie:inception->belongs_to->genre:thriller;
RELATE movie:matrix->belongs_to->genre:sci_fi;
RELATE movie:matrix->belongs_to->genre:action;
RELATE movie:interstellar->belongs_to->genre:sci_fi;
RELATE movie:interstellar->belongs_to->genre:drama;
RELATE movie:blade_runner->belongs_to->genre:sci_fi;
RELATE movie:blade_runner->belongs_to->genre:thriller;
RELATE movie:parasite->belongs_to->genre:drama;
RELATE movie:parasite->belongs_to->genre:thriller;
RELATE movie:joker->belongs_to->genre:drama;
RELATE movie:joker->belongs_to->genre:crime;
RELATE movie:fight_club->belongs_to->genre:drama;
RELATE movie:fight_club->belongs_to->genre:thriller;
RELATE movie:pulp_fiction->belongs_to->genre:crime;
RELATE movie:pulp_fiction->belongs_to->genre:drama;

