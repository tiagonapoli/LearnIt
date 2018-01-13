CREATE TABLE users(
	id int primary key,
	messages_per_day integer
);

CREATE TABLE languages(
	user_id int,
	language_name varchar(50),
	primary key (user_id, language_name),
	foreign key (user_id) references users(id) ON DELETE CASCADE
);

CREATE TABLE words(
	user_id int,
	language varchar(50),
	foreign_word varchar(50),
	english_word varchar(50),
	primary key (user_id, language, foreign_word),
	foreign key (user_id, language) references languages(user_id, language_name) ON DELETE CASCADE
);

CREATE TABLE images(
	user_id int,
	language varchar(50),
	foreign_word varchar(50),
	image_id serial,
	image_path varchar(50),
	primary key (user_id, language, foreign_word, image_id),
	foreign key (user_id, language, foreign_word) references words(user_id, language, foreign_word) ON DELETE CASCADE
);