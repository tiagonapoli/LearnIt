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
	username varchar(50),
	public int DEFAULT 0,
	native_language int DEFAULT 0
);

CREATE TABLE subjects(
	user_id int,
	subject varchar(50),
	
	primary key (user_id, subject),
	foreign key (user_id) references users(id) ON DELETE CASCADE
);

CREATE TABLE topics(
	user_id int,
	subject varchar(50),
	topic varchar(50),

	primary key (user_id, subject, topic),
	foreign key (user_id, subject) references subjects(user_id, subjects) ON DELETE CASCADE
);

CREATE TABLE words(
	user_id int,
	word_id int,
	subject varchar(50),
	topic varchar(50),
	word varchar(300),
	type int, 

	UNIQUE(user_id, subject, topic, word),
	primary key (user_id, word_id),
	foreign key (user_id, subject, topic) references topics(user_id, subject, topic) ON DELETE CASCADE
);


CREATE TABLE cards(
	user_id int,
	word_id int,
	subject varchar(50),
	topic varchar(50),
	word varchar(300),
	card_id int,
	type int,
	content_path varchar(300),
	
	attempts int,
	easiness_factor double precision DEFAULT 1.3,
	interval double precision,
	next_date date,

	UNIQUE(user_id, card_id),
	primary key (user_id, word_id, card_id),
	foreign key (user_id, word_id) references words(user_id, word_id) ON DELETE CASCADE	

);
