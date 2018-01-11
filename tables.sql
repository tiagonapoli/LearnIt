CREATE TABLE users(
	id int primary key,
	messages_per_day integer
);

CREATE TABLE word(
	user_id int,
	word varchar(50),
	primary key (user_id, word),
	foreign key (user_id) references users(id)
);

CREATE TABLE image(
	user_id int,
	word varchar(50),
	id serial,
	img_path varchar(50),
	primary key (user_id, word, id),
	foreign key (user_id, word) references word(user_id, word)
);