deploy-to-board:
	ampy put grandma/main.py
	ampy put grandma/board.py
	ampy put grandma/access.py

create-db:
	python -c "from grandma.bot import start_db; start_db()"

run:
	FLASK_APP=grandma/server.py flask run  --host=0.0.0.0

tests:
	pytest tests

wake:
	source venv/bin/activate
	source .env
