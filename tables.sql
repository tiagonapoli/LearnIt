CREATE TABLE users(
	id int primary key,
	messages_per_day int DEFAULT 0,
	highest_word_id int DEFAULT 0
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
	user_word_id int,

	attempts int,
	easiness_factor double precision DEFAULT 2.5,
	interval double precision,
	next_date date,

	UNIQUE (user_id, user_word_id),
	primary key (user_id, language, foreign_word),
	foreign key (user_id, language) references languages(user_id, language_name) ON DELETE CASCADE
);

CREATE TABLE content(
	user_id int,
	language varchar(50),
	foreign_word varchar(50),
	user_word_id int,

	type varchar(10),
	counter int,
	content_path varchar(50),
	UNIQUE (user_id, user_word_id, counter),
	
	primary key (user_id, language, foreign_word, counter),
	foreign key (user_id, language, foreign_word) references words(user_id, language, foreign_word) ON DELETE CASCADE,
	foreign key (user_id, user_word_id) references words(user_id, user_word_id) ON DELETE CASCADE
);