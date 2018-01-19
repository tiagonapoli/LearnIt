CREATE TABLE users(
	id int primary key,
	messages_per_day int DEFAULT 0,
	highest_word_id int DEFAULT 0,
	highest_card_id int DEFAULT 0,
	highest_archive_id int DEFAULT 0,
	state int DEFAULT 0,
	state2 int DEFAULT 0
);

CREATE TABLE languages(
	user_id int,
	language_name varchar(50),
	
	primary key (user_id, language_name),
	foreign key (user_id) references users(id) ON DELETE CASCADE
);

CREATE TABLE words(
	user_id int,
	user_word_id int,
	language varchar(50),
	topic varchar(50),
	foreign_word varchar(50),

	
	UNIQUE (user_id, language, user_word_id),
	primary key (user_id, language, foreign_word),
	foreign key (user_id, language) references languages(user_id, language_name) ON DELETE CASCADE
);

CREATE TABLE cards(
	user_id int,
	user_word_id int,
	language varchar(50),
	topic varchar(50),
	foreign_word varchar(50),
	user_card_id int,
	type varchar(10),
	
	attempts int,
	easiness_factor double precision DEFAULT 2.5,
	interval double precision,
	next_date date,

	UNIQUE(user_id, user_card_id),

	primary key (user_id, language, user_word_id, user_card_id),
	foreign key (user_id, language, user_word_id) references words(user_id, language, user_word_id) ON DELETE CASCADE	

);

CREATE TABLE archives(
	user_id int,
	user_card_id int,
	counter int,
	type varchar(10),
	content_path varchar(50),
	

	UNIQUE (user_id, user_card_id, counter),
	primary key (user_id, user_card_id, counter),
	foreign key (user_id, user_card_id) references cards(user_id, user_card_id) ON DELETE CASCADE
);
