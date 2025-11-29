.PHONY: build migrate run gen-session

build:
	docker build --target app -t heartbeat .

migrate:
	docker build --target migrate -t heartbeat-migrate .
	docker run --rm -v ./data:/data heartbeat-migrate

run:
	docker run --rm -v ./data:/data:ro --env-file .env heartbeat

gen-session:
	uv run python scripts/gen_session.py