## Contributing to Tube Archivist

Welcome, and thanks for showing interest in improving Tube Archivist!  
If you haven't already, the best place to start is the README. This will give you an overview on what the project is all about.

## Report a bug

If you notice something is not working as expected, check to see if it has been previously reported in the [open issues](https://github.com/tubearchivist/tubearchivist-metrics/issues).
If it has not yet been disclosed, go ahead and create an issue.  
If the issue doesn't move forward due to a lack of response, I assume it's solved and will close it after some time to keep the list fresh. 

## Dev setup

Setup your environment, e.g. with python venv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Setup pre-commit for linting:
```bash
pre-commit install
```

## Build container and release
Test building your container:
```
docker buildx build --load -t bbilly1/tubearchivist-metrics .
```

To test the multi arch container is building, run:

```
docker buildx build --platform linux/amd64,linux/arm64 -t bbilly1/tubearchivist-metrics .
```

To release:

- Create a git tag
- Push the tag
- Create a Release on [Github](https://github.com/tubearchivist/tubearchivist-metrics/releases/new)
- Then the webhook will trigger to build and push a new container to [docker hub](https://hub.docker.com/r/bbilly1/tubearchivist-metrics).
