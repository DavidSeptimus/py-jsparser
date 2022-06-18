.PHONY: clean clone-langs build-langs run clean-build docker-build docker-run docker install init

.EXPORT_ALL_VARIABLES:

PIPENV_VERBOSITY=-1

all: clean clone-langs build-langs run


clean-build:
	rm -rf ./build

clean: clean-build
	rm -rf ./languages


clone-langs:
	. ./scripts/clone_languages.sh

build-langs:
	pipenv run python ./scripts/build_languages.py

install:
	pipenv install -d

init: clone-langs install build-langs

run:
	pipenv run python jsparser/jsparser.py --source-path resources/app.js --module "fs/promises" --property "readFile"

docker-build:
	docker compose build

docker-run:
	docker compose up

docker: clean clone-langs docker-build docker-run
