CREATE TABLE Lexeme (
	lexid		int not null auto_increment primary key,
	lex 		text
);

CREATE TABLE Lemma (
	lemid		int not null auto_increment primary key,
	lemtype		char,
	lem			text,
	suffix		text,
	tag			text,
	descr		text,
	lexid 		int not null references Lexeme(lexid)
);