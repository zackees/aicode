# aicode

The most advanced ai coding tool on the planet.

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)

[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)


# About

Okay well `aider.chat` is by far the BEST aicoding assistant on the planet. But `aicode`, a front end for
`aider.chat` is EASIER TO USE! So use this whenever you can for Windows/Linux/MacOS.
Think of `aicode` as `aider.chat` but on easy mode.

One foot gun here is that `aider.chat` only works on files in a git repo. therefore you must be in a git repo
for `aicode` to work. This is required because `aider.chat` will generate a repo map as part of the query.


## Usage:

```bash
pip install advanced-aicode
aicode
```

### Note

The package name is NOT the same as the command tool. The package is `advanced-aicode` and the tool is called `aicode`. Someone
else grabbed package name `aicode` over a year ago and this is the best name I could come up with to get it into pypi.


# aicode is better than aider.chat in the following ways


  * `aicode` is easier to install. Like WAY easier. It will tell you what you need to do to complete the installation, such
    as setting the api key if none are detected.
  * `aicode` will not f@ck up your global pip environment. We fix this by lazily installing `aider.chat` using `pipx`
  * `aicode` will change the directory to a the project root containing a `.git` directory. `aider.chat` will just fail to run.
  * `aicode` will default to NOT creating a git commit on every change. Instead it will
    just raw dog it to your current repo. This simplifies usage because most of the time you will
    only be editing one file and if you don't like the change you can just invoke undo on the file.
    If you want to create a git commit on every change (so that you can use /undo)
    then pass in `aicode -a`. This works better if you are editing multiple files and want and want
    to step back in history, must most of the time it's better to just let `aicode` work on one file
    at a time.
  * `aicode` has the benefit of allowing easy upgrades to `aider.chat` from the command line using `aicode --update` which will
    invoke `pipx` update on the backend.
  * `aicode` will default to using `ChatGPT4-o` if it detects you have have an openapi key.
  * `aicode` will save and insert the environmental variables on demand. `aider.chat` requires that you
    insert these variables in your `~/.bashrc` file (linux) or the equivalent for Windows and MacOS.
  * `aicode` will check for new versions in the background and inform you of an update on the NEXT run of
    `aicode` and the command line you can use. This was a feature that `aider.chat` program actually implemented for this project.
  * `aicode` will ask you to modify the `.gitignore` file so that you aren't uploading your f*cking chat
    history to your repo by default.

Happy CODING!

# Releases

  * 1.1.6 - Fixes has update when the versions match
  * 1.1.5 - Fixes `--just-check-update` which had a typo in the last version as `--just-check-updated`
  * 1.1.4 - Fixes `aider --check-update` with `--just-check-update`
  * 1.1.3 - Fixes `aider --skip-check-update` which is now `--no-check-update`
  * 1.1.1 - Fix a infinit recursion loop while trying to find the .git directory.
  * 1.1.0 - The --slow, --fast, --claude3 are not long used. Now it's just --chatgpt and --claude.
  * 1.0.4 - If `--upgrade` fails, then attempt recovery by asking the user to upgrade `pipx` and then try again.
  * 1.0.3 - Improved version parsing so that stuff like X.X.X-dev can be parsed.
  * 1.0.2 - `--claude3`` now maps to sonnet mode. This is now the default if both keys are present for claude3 and openai.
  * 1.0.1 - Improve readme.
  * 1.0.0 - Initial release.