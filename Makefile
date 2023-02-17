docker:
    DOCKER_BUILDKIT=1 docker build -t verifier --ssh default -f Dockerfile  .

.PHONY docker
