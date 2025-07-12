up:
	docker compose up --build

up-d:
	docker compose up -d

down:
	docker compose down

exec:
	docker compose exec web bash

logs:
	docker compose logs
