FROM python:3.8-bullseye

RUN mkdir /usr/src/util

WORKDIR /usr/src/util

COPY Pipfile* .

RUN pip3 install pipenv

RUN pipenv install --system --dev

WORKDIR /usr/src/app

# Rebuilds the languages library and runs the jsparser script.
# That's what I get for developing on Windows. :(
CMD rm -rf ./build && \
 python ./scripts/build_languages.py && \
 python jsparser/jsparser.py --source-path resources/app.js --module "fs/promises" --property "readFile"
