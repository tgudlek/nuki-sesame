# nuki-sesame [![Version](https://img.shields.io/github/v/tag/tgudlek/nuki-sesame.svg)](https://github.com/tgudlek/nuki-sesame/releases)

A basic command-line interface for interacting with the Nuki Web API.

## Installation

Ensure you have Python 3.8 installed, and it's recommended to use a virtual environment.

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install `poetry`:

```bash
pip install poetry
```

Install the required packages:

```bash
poetry install --no-dev
```

### Install `nuki-sesame` globally

To use `nuki-sesame` from any location on your system, you can create a shell alias. 
This can be done by adding the following line to your shell configuration file (`.bashrc` for Bash, `.zshrc` for Zsh, etc.):

```bash
alias nuki-sesame="/path/to/project/.venv/bin/python /path/to/project/nuki-sesame.py"
```

Replace `/path/to/project/` with the actual path to your `nuki-sesame` project directory.

If you would like to generate the alias from the current working directory, use the following command:

```bash
echo "alias nuki-sesame=\"$(pwd)/.venv/bin/python $(pwd)/nuki-sesame.py\""
```

Now, take the output of this command and add it to your shell configuration file.
After you've added it, you will need to source the shell configuration file, and you're good to go.
Now, you should be able to use the `nuki-sesame` command from any location on your system.

## Usage

If you're only calling the tool from the directory you've installed it in, you should use `./nuki-sesame.py`. 
If you've [installed the tool globally](#install-nuki-sesame-globally), you can also use `nuki-sesame` anywhere.

The command line interface provides several commands and subcommands. You can use `--help` with any command to see its usage. 
Here are some examples:

### Authenticate and save the token

```bash
./nuki-sesame.py auth
```

### Check the validity of the token

```bash
./nuki-sesame.py auth --check_only
```

### Lock/unlock a smartlock

In case you have a single smartlock:
```bash
./nuki-sesame.py lock
```

In case you have a multiple smartlocks:
```bash
./nuki-sesame.py unlock --smartlock_id 123456
```

### Add an authorization code to a smartlock

In case you have a single smartlock, and wish to generate any code:
```bash
./nuki-sesame.py code add --duration 1h
```

In case you have a single smartlock, and wish to generate a specific code:
```bash
./nuki-sesame.py code add --code 987654 --duration 1h
```

In case you have a multiple smartlocks, and wish to generate a specific code:
```bash
./nuki-sesame.py code add --smartlock_id 123456 --code 987654 --duration 1h
```

### Delete an authorization code from a smartlock

In case you have a single smartlock, and wish to pick a code to delete:
```bash
./nuki-sesame.py code delete
```

In case you have a single smartlock, and wish to delete a specific code:
```bash
./nuki-sesame.py code delete --code 987654
```

In case you have a multiple smartlocks, and wish to delete a specific code:
```bash
./nuki-sesame.py code delete --smartlock_id 123456 --code 987654
```

## Contributing

Contributions to the Nuki CLI project are welcome! 
However, please note that we make no guarantees regarding the acceptance or inclusion of all contributions. 
Be sure to adhere to coding standards and conventions, and maintain a respectful and inclusive environment. 
Thank you for your interest in improving the Nuki CLI!

### Code Formatting

We use Black as our Python code formatter to ensure consistent code style throughout the project. To format your code, follow these steps:

1. Install dev dependencies using `poetry`:

```bash
poetry install --dev
```

2. Navigate to the project directory and run the following command to format your code:

```bash
black .
```

This will automatically format all Python files in the project directory according to the Black code style guidelines.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). 
Feel free to use the code in any way you see fit, without any warranties or guarantees of correctness.
