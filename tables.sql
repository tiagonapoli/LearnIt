CREATE TABLE users(
	id int primary key,
	messages_per_day integer
);

CREATE TABLE words(
	user_id int,
	idiom varchar(50),
	foreign_word varchar(50),
	english_word varchar(50),
	primary key (user_id, idiom, foreign_word),
	foreign key (user_id) references users(id) ON DELETE CASCADE
);

CREATE TABLE images(
	user_id int,
	idiom varchar(50),
	foreign_word varchar(50),
	id serial,
	img_path varchar(50),
	primary key (user_id, idiom, foreign_word, id),
	foreign key (user_id, idiom, foreign_word) references words(user_id, idiom, foreign_word) ON DELETE CASCADE
);