deploy-to-board:
	ampy put grandma/main.py
	ampy put grandma/board.py
	ampy put grandma/access.py

run:
	FLASK_APP=grandma/server/main.py flask run  --host=0.0.0.0

tests:
	pytest tests
