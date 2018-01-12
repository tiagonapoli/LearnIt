CREATE TABLE users(
	id int primary key,
	messages_per_day integer
);

CREATE TABLE word(
	user_id int,
	english_word varchar(50),
	foreign_word varchar(50),
	primary key (user_id, english_word, foreign_word),
	foreign key (user_id) references users(id) ON DELETE CASCADE
);

CREATE TABLE image(
	user_id int,
	english_word varchar(50),
	foreign_word varchar(50),
	id serial,
	img_path varchar(50),
	primary key (user_id, english_word, foreign_word, id),
	foreign key (user_id, english_word, foreign_word) references word(user_id, english_word, foreign_word) ON DELETE CASCADE
);