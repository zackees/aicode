# aicode

[![Linting](../../actions/workflows/lint.yml/badge.svg)](../../actions/workflows/lint.yml)

[![MacOS_Tests](../../actions/workflows/push_macos.yml/badge.svg)](../../actions/workflows/push_macos.yml)
[![Ubuntu_Tests](../../actions/workflows/push_ubuntu.yml/badge.svg)](../../actions/workflows/push_ubuntu.yml)
[![Win_Tests](../../actions/workflows/push_win.yml/badge.svg)](../../actions/workflows/push_win.yml)

Despite the lack of stars, this is the best open source coding assistant you can use. See below for why.

![406264279-ddb746de-0a02-4867-b9da-2b2056eb5649](https://github.com/user-attachments/assets/18b1c918-c0b8-43ba-9f24-24af9f31ca3a)


# About


## Usage:

```bash
pip install advanced-aicode
aicode
```

Why is this the best open source coding assistant? Because this is a front end for [aider.chat](https://aider.chat), but with all the sharp edges filed off and the defaults you want, included automatically.

Features
  * `aicode` is easier to install. Like WAY easier.
  * `aicode` will not f@ck up your global pip environment.
  * `aicode` will notify you of updates, invoke it with`--update`
  * `aicode` will always turn on aider.chat's architect mode, which has significantly higher coding performance than non architect mode.
  * `aicode` always invokes `--watch` mode, unless you shut it off via `--no-watch`

### Watch mode

Before watch mode, you had to manually add files to the chat terminal, then tell aider what you wanted to do. Now aider will watch the files and look for comments that container AI! in it, then follow the instructions.

So for example, say you have this piece of code

```python
def list_files(root: Path) -> list[Path]:
  pass
```
Now let's say you want to implement this function. You will fire up `aicode` and type in a comment that ends with `AI!` in it, which the ai will see.

```python
def list_files(root: Path) -> list[Path]"
  pass # please implement this AI!
```

Aider will automatically see this and start editing the file!

### Note

The package name is NOT the same as the command tool. The package is `advanced-aicode` and the tool is called `aicode`. Someone
else grabbed package name `aicode` over a year ago and this is the best name I could come up with to get it into pypi.

Happy CODING!


# Releases
  * 2.1.0 - When using `--deep` mode, prefer to use `o3`, per aider-chat benchmarks for the winner in the polyglot test (6/3/2025).
  * 2.0.35 - Bunch of errors fixed. Upgrading and purging is now safer. New aider-chat backend installs are located in incrementing folders.
  * 2.0.30 - Architect mode is now off by default. It's not general purpose. To switch it on, use `--deep`
  * 2.0.18 - Internal refactor to make interactive usage of aider.chat easier to deal with.
  * 2.0.6 - Asking for restoring history is now disabled always.
  * 2.0.5 - Watchmode now enabled by default.
  * 2.0.4 - New sonnet model anthropic/claude-3-5-sonnet-20241022 is now the default for claude mode.
  * 2.0.3 - Now using Semi secret instead of keyring, which encrypts the key at a secret location.
  * 2.0.2 - If there is chat history then aicode will ask if you want to restore it.
  * 2.0.1 - Implement disabling of git if a git directory can't be found.
  * 2.0.0 - Implemented aider's new "architect" mode, which although is a small change in the code, does change how the product is used.
            Disable this by using `--no-architect` to get the old behavior.
  * 1.2.16 - Linting is disable by default
  * 1.2.15 - Aider is now installed in a side package. This means Aider won't be cleared when you uninstall `advanced-aicode` but should resolve the issue with OSX throwing exceptions for locked files. See `aicode --purge`
  * 1.2.14 - Fixes wrong VIRTUAL ENV path.
  * 1.2.13 - Fixes KeyboardInterrupt exception in trampoline.
  * 1.2.12 - Final fixes (I hope) in this cycle.
  * 1.2.11 - Fixes some issues with warnings being emitted.
  * 1.2.10 - Adds missing `setuptools` dependency that was causing a non fatal error.
  * 1.2.9 - Now uses trampoline to re-root the cwd when calling the program. Fixes Linux/MacOS.
  * 1.2.8 - `aicode --upgrade` now more robust. Also fixed a path issue on windows.
  * 1.2.7 - `aicode --upgrade` has been fixed to work with `uv` package upgrades.
  * 1.2.6 - Re-rooting trick fails for mac/linux, only apply it for win32
  * 1.2.5 - Cwd directory is inserted so aider-chat backend is invoked from the current command line.
  * 1.2.4 - Switch isolated environment to an ad-hoc usage of `uv`. Much faster and better!
  * 1.2.3 - Fixes a win32 bug related to `isolated-environment`
  * 1.2.2 - Propagate fixes from `isolated-environment` to fix Mac/Linux
  * 1.2.1 - Buf fix for isolated-environment by using `shell=True`.
  * 1.2.0 - Aider is now installed with `isolated-environment` instead of `pipx` for better isolation. We now use `keyring` to securely store your api keys.
  * 1.1.8 - Custom path now set for pipx, should fix most pipx issues.
  * 1.1.7 - Version detection fixed now that the api has been made much better.
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
