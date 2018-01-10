CREATE TABLE users(
	id int primary key,
	messages_per_day integer
);

CREATE TABLE vocabulary(
	user_id varchar(20) references users(id),
	english_name varchar(20),
	local_name varchar(20),
	primary key (user_id, english_name)
);

CREATE TABLE word(
	user_id varchar(20),
	vocabulary varchar(20),
	word varchar(20),
	primary key (user_id, vocabulary, word),
	foreign key (user_id, vocabulary) references vocabulary(user_id, english_name)
);

CREATE TABLE image(
	user_id varchar(20),
	vocabulary varchar(20),
	word varchar(20),
	id serial,
	img_path varchar(50),
	primary key (user_id, vocabulary, word, id),
	foreign key (user_id, vocabulary, word) references word(user_id, vocabulary, word)
);