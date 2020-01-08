# YouTube Playlist Downloader
## Requirements
Development for this project requires *Miniconda* or *Conda* for development isolation, GNU Make and Visual Studio Code as an IDE.
* Miniconda: [Download](https://docs.conda.io/en/latest/miniconda.html) for your OS. Make sure *conda* executable is in your PATH.
* Visual Studio Code: [Download](https://code.visualstudio.com/) for your OS. Install following extensions:
  * [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
  * [Markdown All in one](https://marketplace.visualstudio.com/items?itemName=yzhang.markdown-all-in-one)
  * [autoDocstring](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring)
  * [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
* GNU Make
  * [Linux](https://www.gnu.org/software/make/)
  * [Mac](https://developer.apple.com/xcode/)

## Setup
Follow [README](README.md) to create Google project and collect client secrets.
Follow [gitlab's documentation](https://docs.gitlab.com/ee/ssh/) to setup password free ssh.
Run following command to set up conda environment.
```bash
make setup
```
Open Visual Studio Code workspace using *vscode.code-workspace* file.
Choose conda python version on the bottom left side of window.

## Development
Create a branch off of `master` and make necessary changes. Run appropriate commands in following sections. When ready, follow [Release](#release) guidelines.

### Test
```bash
make validate
make test
make coverage
```
### Doc
```bash
make doc
```

### Run
You can modify [init.mk](init.mk) to change your development configuration.

```bash
make run
```

### Docker
CI/CD pipeline on Gitlab uses docker container. 
After making changes to [Dockerfile](Dockerfile), run
```bash
make docker-push
```

If you want to test docker container or want to have build server environment,
run following command:
```bash
make console
```

### Clean
```bash
make clean
```

## Release
Create a pull request to merge your branch to `master`.
Make sure to use option to squash commits and delete branch after merge.
The project has content delivery pipeline buit into it.
When the pull request is approved and merged, packages will be auto released
to *PyPI*.

## Documentation
Package documentation for the latest release is available at
[https://planetsoni.gitlab.io/youtubeplaylistdownloader](https://planetsoni.gitlab.io/youtubeplaylistdownloader/).
