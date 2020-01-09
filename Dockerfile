FROM python:3.7.5-alpine3.10 as base

WORKDIR /app
RUN apk add --update make
RUN pip3 install pipenv==2018.11.26

# Copying all the file in repo except the ones in .dockerignore
COPY . .
# pipenv install dependencies and fwfparser package, system wide without creating a venv
RUN pipenv install --system --deploy

# The `Prod` stage is push to dockerhub ang tagged as latest if all tests/checks pass in ci without failure - cleaning unnecessary files from base here
# The resulting image will parse an example using example/parse_example.py
FROM base as Prod
RUN ls | grep -vE "example" | xargs rm -r

CMD ["-s", "example/spec.json", "-o", "example/output.csv"]

ENTRYPOINT [ "python3", "-m", "fwfparser" ]

# The `Security` stage checks Prod container image for vulnerabilities using the Aqua MicroScanner. This requires providing a build-arg with your MicroScanner token
# See: https://github.com/aquasecurity/microscanner
FROM Prod as Security
ARG MICROSCANNER
RUN apk add --no-cache ca-certificates \
    && update-ca-certificates \
    && wget https://get.aquasec.com/microscanner -O /microscanner \
    && echo "8e01415d364a4173c9917832c2e64485d93ac712a18611ed5099b75b6f44e3a5  /microscanner" | sha256sum -c - \
    && chmod +x /microscanner
RUN /microscanner ${MICROSCANNER} --full-output

# The `test-base` stage is used as the base for images that require the development dependencies.
FROM base as test-base
RUN pipenv install --system --deploy --dev

# The `Check` stage runs a check of the installed package dependencies against a list of known security vulnerabilities. The build will fail if vulnerabilities are found
# See: https://github.com/pyupio/safety
FROM test-base AS Check
RUN safety check

# The `Test` stage runs the application unit tests, the build will fail
# if the tests fail.
FROM test-base as Test
RUN pytest -v
CMD [ "-v" ]
ENTRYPOINT [ "pytest"]