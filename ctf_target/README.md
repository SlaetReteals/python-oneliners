# Cyber CTF Reconnaissance Target Environment

This directory (`ctf_target`) contains simulated vulnerable configuration files, flags, credentials, database dumps, and server artifacts designed for penetration testing and CTF tool testing.

## Included Simulated Assets:
- `home/user_flag.txt` & `root_flag.md` (Capture The Flag targets)
- `config/db_passwords.txt` & `config/aws_creds.ini` (Exposed credentials)
- `secrets/client_secrets.json` (Exposed tokens & OAuth keys)
- `web/.env.local` & `web/wp-config.php` (Dotenv and web framework configs)
- `keys/id_rsa.key` & `keys/server_cert.pem` (Cryptographic keys & certs)
- `db/users_dump.sql` & `db/app_storage.db` (SQL database backups)
- `web/index.php.bak` & `backups/settings.py.old` (Unpatched backup file discoveries)
- `home/.bash_history` (Terminal command histories containing leaked passwords)
- `web/index.html` (Web root pages with left-behind HTML developer comments)

*Note: These files are automatically built into the browser's WebAssembly (WASM) virtual filesystem when loading the PyScript Hub!*
