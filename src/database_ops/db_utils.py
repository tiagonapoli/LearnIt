from flashcard import Card, Word

def create_card_with_row(row):
	return Card(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10])

def create_word_with_row(row):
	return Word(row[0], row[1], row[2], row[3], row[4])