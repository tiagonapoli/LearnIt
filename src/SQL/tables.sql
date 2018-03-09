CREATE TABLE users(
	user_id int primary key,
	username varchar(50),
	active int DEFAULT 1,
	native_language int DEFAULT 0,
	public int DEFAULT 0,
	state1 int DEFAULT 0,
	state2 int DEFAULT -1,
	highest_card_id int DEFAULT 0,
	highest_study_item_id int DEFAULT 0,
	cards_per_hour int DEFAULT 3,
	review_questions_per_day int DEFAULT 40,
	learning_cards_per_day int DEFAULT 5, 
	card_waiting int DEFAULT 0,
	card_waiting_type int DEFAULT 0,
	grade_waiting_for_process int DEFAULT 0
);

CREATE TABLE subjects(
	user_id int,
	active int DEFAULT 1, 
	subject varchar(50),

	primary key (user_id, subject),
	foreign key (user_id) references users(user_id) ON DELETE CASCADE
);

CREATE TABLE topics(
	user_id int,
	active int DEFAULT 1,
	subject varchar(50),
	topic varchar(50),

	primary key (user_id, subject, topic),
	foreign key (user_id, subject) references subjects(user_id, subject) ON DELETE CASCADE
);

CREATE TABLE study_items(
	user_id int,
	study_item_id int,
	active int DEFAULT 1,  
	subject varchar(50),
	topic varchar(50),
	study_item varchar(300),
	study_item_type int,

	UNIQUE(user_id, subject, topic, study_item),
	primary key (user_id, study_item_id),
	foreign key (user_id, subject, topic) references topics(user_id, subject, topic) ON DELETE CASCADE
);


CREATE TABLE cards(
	user_id int,
	study_item_id int,
	active int DEFAULT 1,
	subject varchar(50),
	topic varchar(50),
	study_item varchar(300),
	study_item_type int, 
	card_id int,
	question varchar(300),
	question_type varchar(10),
	
	attempts int,
	easiness_factor double precision,
	interval double precision,
	next_date date,

	primary key (user_id, card_id),
	foreign key (user_id, study_item_id) references study_items(user_id, study_item_id) ON DELETE CASCADE	

);