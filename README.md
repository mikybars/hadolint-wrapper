# hadolint-wrapper

## What is hadolint?

[Hadolint](https://github.com/hadolint/hadolint) stands for Haskell Dockerfile Linter and is:

> A smarter Dockerfile linter that helps you build [best practice](https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices) Docker images. 

## Example

### Dockerfile

```dockerfile
FROM debian
RUN export node_version="0.10" \
&& apt-get update && apt-get -y install nodejs="$node_verion"
COPY package.json usr/src/app
RUN cd /usr/src/app \
&& npm install node-static

EXPOSE 80000
CMD "npm start"
```

### With hadolint

```
$ hadolint Dockerfile
Dockerfile:1 DL3006 Always tag the version of an image explicitly
Dockerfile:2 SC2154 node_verion is referenced but not assigned (did you mean 'node_version'?).
Dockerfile:2 DL3009 Delete the apt-get lists after installing something
Dockerfile:2 DL3015 Avoid additional packages by specifying `--no-install-recommends`
Dockerfile:5 DL3003 Use WORKDIR to switch to a directory
Dockerfile:5 DL3016 Pin versions in npm. Instead of `npm install <package>` use `npm install <package>@<version>`
Dockerfile:8 DL3011 Valid UNIX ports range from 0 to 65535
Dockerfile:9 DL3025 Use arguments JSON notation for CMD and ENTRYPOINT arguments
```

### With hadolint wrapper

```bash
$ hadolintw Dockerfile
```

![sample-output](https://user-images.githubusercontent.com/43891734/76677889-a3de9680-65d3-11ea-9575-8ba289bcb149.png)

## Installation

```
$ pip install hadolintw
```

## Usage

```
$ hadolintw
Usage: hadolintw [OPTIONS] DOCKERFILE [HADOLINT_ARGS]...

  Provides a more clear output for hadolint

Options:
  -d, --use-docker             use the dockerized version of hadolint
  --color [never|auto|always]
  --help                       Show this message and exit.
```

Set up as a wrapper:

```
$ alias hadolint=hadolintw
$ hadolint Dockerfile --ignore DL3020
# Please note that all hadolint options must come AFTER the Dockerfile
```

## FAQ

### Does the wrapper keep the exit status of hadolint so that I can use it in my CI environment?

No problem.

### My CI environment doesn't support colorized output. Can I disable it?

By default the wrapper can detect if the output is being written to a tty or a pipe or a file, enabling or disabling the color codes accordingly (`—color auto` is the default setting). However you can always turn this feature on or off regardless of the type of output destination:

```
$ hadolintw --color never Dockerfile
```

### In our team we have a `hadolint.yml` with some rules defined for our project. Can we still use it with the hadolint wrapper?

Sure.

```
$ hadolintw Dockerfile --config hadolint.yml
```

### The hadolint program is not available where my build is going to run but at least I have access to a Docker environment. Can I still run hadolint?

[Be my guest](https://hub.docker.com/r/hadolint/hadolint).

```
$ hadolintw --use-docker Dockerfile
Unable to find image 'hadolint/hadolint:latest' locally
latest: Pulling from hadolint/hadolint
8a8460b25d70: Pulling fs layer
8a8460b25d70: Verifying Checksum
8a8460b25d70: Download complete
8a8460b25d70: Pull complete
Digest: sha256:0cdbd1e0f5fd3135d17617bb510a85c0248eb70b041021fe5431d4d1501d41b9
Status: Downloaded newer image for hadolint/hadolint:latest
...
```

