# classcharts_export
Export data from classcharts.com

## Install
Clone the repo
 - `git clone https://github.com/darrengoulden/classcharts_export.git`
 - `git clone git@github.com:darrengoulden/classcharts_export.git`

Install the requirements
- `pip install -r requirements.txt`

Install dotenvx
- See https://dotenvx.com/docs/install

Modify the env file
```
email="email@address.com"
password="your_password"
```

Encrypt the env file
- `dotenvx encrypt`

## Usage

Run the script
- `dotenvx run -- python main.py`

Print help
- `dotenvx run -- python main.py -h`

Get student activity
- `dotenvx run -- python main.py activity`
- `dotenvx run -- python main.py activity --days <int>`
- `dotenvx run -- python main.py activity --csv true`
- `dotenvx run -- python main.py activity -h`

Get student behaviour
- `dotenvx run -- python main.py behaviour`
- `dotenvx run -- python main.py behaviour --days <int>`
- `dotenvx run -- python main.py behaviour -h`

Get student homework
- `dotenvx run -- python main.py homework`
- `dotenvx run -- python main.py homework --days <int>`
- `dotenvx run -- python main.py homework --display_date choices=['issue_date', 'due_date']`
- `dotenvx run -- python main.py homework --number <int>`
- `dotenvx run -- python main.py homework -h`
