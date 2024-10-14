.PHONY: docker tests

docker:
	DOCKER_BUILDKIT=1 docker build -t verifier --ssh default -f Dockerfile  .

tests:
	VERIFIER_TEST=1 python -m unittest discover tests
