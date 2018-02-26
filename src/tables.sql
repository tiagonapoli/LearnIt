CREATE TABLE users(
	id int primary key,
	active int DEFAULT 1,
	cards_per_hour int DEFAULT 3,
	review_cards_per_day int DEFAULT 40,
	learning_words_per_day int DEFAULT 5, 
	highest_word_id int DEFAULT 0,
	highest_card_id int DEFAULT 0,
	highest_archive_id int DEFAULT 0,
	state1 int DEFAULT 0,
	state2 int DEFAULT -1,
	state3 int DEFAULT -1,
	card_waiting int DEFAULT 0,
	card_waiting_type int DEFAULT 0,
	grade_waiting_for_process int DEFAULT 0,
	username varchar(30),
	public int DEFAULT 0
);

CREATE TABLE languages(
	user_id int,
	language_name varchar(50),
	
	primary key (user_id, language_name),
	foreign key (user_id) references users(id) ON DELETE CASCADE
);

CREATE TABLE topics(
	user_id int,
	language varchar(50),
	topic varchar(50),

	primary key (user_id, language, topic),
	foreign key (user_id, language) references languages(user_id, language_name) ON DELETE CASCADE
);

CREATE TABLE words(
	user_id int,
	user_word_id int,
	language varchar(50),
	topic varchar(50),
	foreign_word varchar(200),

	UNIQUE(user_id, language, topic, foreign_word),
	primary key (user_id, user_word_id),
	foreign key (user_id, language, topic) references topics(user_id, language, topic) ON DELETE CASCADE
);

CREATE TABLE specialwords(
	users_using int DEFAULT 1,
	archive varchar(200),
	primary key (archive)
);

CREATE TABLE cards(
	user_id int,
	user_word_id int,
	language varchar(50),
	topic varchar(50),
	foreign_word varchar(50),
	user_card_id int,
	type varchar(20),
	
	attempts int,
	easiness_factor double precision DEFAULT 1.3,
	interval double precision,
	next_date date,

	UNIQUE(user_id, user_card_id),
	primary key (user_id, user_word_id, user_card_id),
	foreign key (user_id, user_word_id) references words(user_id, user_word_id) ON DELETE CASCADE	

);

CREATE TABLE archives(
	user_id int,
	user_card_id int,
	counter int,
	type varchar(20),
	content_path varchar(140),

	primary key (user_id, user_card_id, counter),
	foreign key (user_id, user_card_id) references cards(user_id, user_card_id) ON DELETE CASCADE
);
