FROM python:3.7.5-alpine3.10 as base

WORKDIR /app
RUN apk add --update make
RUN pip3 install pipenv==2018.11.26

# COPY ./fwfparser fwfparser
# COPY ./setup.py setup.py
# COPY LICENSE LICENSE
# COPY VERSION VERSION
# COPY README.md README.md
# COPY ./requirements.txt requirements.txt
# COPY ./example example
# COPY ./tests tests
# COPY ./Makefile Makefile

# Copying all the file in repo except the ones in .dockerignore
COPY . .
# pipenv install dependencies and fwfparser package, system wide without creating a venv
RUN pipenv install --system --deploy

# The `Prod` stage is the default stage if the Dockerfile is run without
# a target stage set. The resulting image will parse an example using example/parse_example.py
FROM base as Prod
RUN ls | grep -vE "example" | xargs rm -r

CMD [ "python3", "example/parse_example.py" ]

# The `test-base` stage is used as the base for images that require the development dependencies. The duplication of the COPY instruction avoids breaking the cache for that later when the Pipfile changes
FROM base as test-base
RUN pipenv install --system --deploy --dev

# The `Test` stage runs the application unit tests, the build will fail
# if the tests fail.
FROM test-base as Test
RUN pytest -v

# The `Check` stage runs a check of the package dependencies against a list of known security vulnerabilities. The build will fail if vulnerabilities are found
FROM test-base AS Check
RUN safety check

# The `Security` stage checks the application for security vulnerabilities using the
# Aqua MicroScanner. This requires providing a build-arg with your MicroScanner token
FROM base as Security
ARG MICROSCANNER
RUN apk add --no-cache ca-certificates \
    && update-ca-certificates \
    && wget https://get.aquasec.com/microscanner -O /microscanner \
    && echo "8e01415d364a4173c9917832c2e64485d93ac712a18611ed5099b75b6f44e3a5  /microscanner" | sha256sum -c - \
    && chmod +x /microscanner
RUN /microscanner ${MICROSCANNER} --full-output