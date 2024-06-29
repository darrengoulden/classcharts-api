# classcharts_export
Export data from classcharts.com

## Instructions
Clone the repo
`git clone https://github.com/darrengoulden/classcharts_export.git'
`git clone git@github.com:darrengoulden/classcharts_export.git`

Install the requirements
`pip install -r requirements.txt'

Install dotenvx
See https://dotenvx.com/docs/install

Modify the env file
```
email="email@address.com"
password="your_password"
```

Encrypt the env file
`dotenvx encrypt`

Run the script
`dotenvx run -- python main.py`

Output the help
`dotenvx run -- python main.py --help`