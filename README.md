# Python-Iam

## load the Environment


```
please note that the ctx argument is commonly used in Click command-line interfaces to pass around contextual information or share data between commands. It's generally good practice to define and use the ctx argument if you intend to utilize it in your command-line interface.
By adding @click.pass_context decorator to the cli() function, Click will automatically pass the click.Context object as the first argument (ctx) to the function. Then, you can set ctx.obj to the obj variable, allowing you to access it within your subcommands using ctx.obj.
```

```bash
source profile.sh
```

```bash
python3 iam.py
```

| Usage                           | iam.py [OPTIONS] COMMAND [ARGS]... |
|---------------------------------|-----------------------------------|
| Options                         |                                   |
| `--help`                        | Show this message and exit.       |
| Commands                        |                                   |
| `create-user`                   |                                   |
| `delete-user`                   |                                   |
| `list-access-keys`              |                                   |
| `list-groups`                   |                                   |
| `list-groups-for-user`          |                                   |
| `list-users`                    |                                   |
| `password-reset`                |                                   |
| `remove-user-from-group`        |                                   |
| `rotate-access-keys`            |                                   |




```bash
python3 iam.py list-groups
```
```
╒══════════╕
│ Groups   │
╞══════════╡
│ Admin    │
╘══════════╛
```
```bash
python3 iam.py create-user vijay --groupname Admin
```
```
User created successfully.
Details:
╒════════════════════╤═══════════════════════════════════════════════════╕
│ Field              │ Value                                             │
╞════════════════════╪═══════════════════════════════════════════════════╡
│ AWS URL            │ https://signin.aws.amazon.com/console/            │
├────────────────────┼───────────────────────────────────────────────────┤
│ Username           │                                                   │
├────────────────────┼────────────────────────────────────-──────────────┤
│ Temporary password │                                                   │
├────────────────────┼───────────────────────────────────────────────────┤
│ Access key ID      │                                                   │
├────────────────────┼───────────────────────────────────────────────────┤
│ Secret access key  │                                                   │
╘════════════════════╧═══════════════════════════════════════════════════╛

```

```bash
python3 iam.py list-groups-for-user --user vijay
```
```
╒══════════════╤═══════════════════════╕
│ Group Name   │ Group ID              │
╞══════════════╪═══════════════════════╡
│ Admin        │             MUERBI6BV │
╘══════════════╧═══════════════════════╛
```
```bash
python3 iam.py list-users
```
```
╒══════════╕
│ Users    │
╞══════════╡
|  vijay   |
╘══════════╛
```

```bash
python3 iam.py list-users --groupname Admin
```
```
╒══════════╕
│ Users    │
╞══════════╡
|  vijay   |
╘══════════╛
```

```bash
python3 iam.py list-access-keys --user vijay
```
```
╒══════════════════════╤══════════╤═════════════════════╤══════════════╕
│ Access Key ID        │ Status   │ Created             │   Age (days) │
╞══════════════════════╪══════════╪═════════════════════╪══════════════╡
│ AKIAUY244            │ Active   │ 2023-05-29 07:15:31 │            0 │
╘══════════════════════╧══════════╧═════════════════════╧══════════════╛
```
```bash
python3 iam.py rotate-access-keys --user vijay
```
```
Deleted access key 'AKIAUY24' for user 'vijay'.
New access key created successfully.
Details:
Access Key ID: AKIAU
Secret Access Key: ldIBkwB9qViuse
╒══════════════════════╤══════════╤═════════════════════╤══════════════╕
│ Access Key ID        │ Status   │ Created             │   Age (days) │
╞══════════════════════╪══════════╪═════════════════════╪══════════════╡
│ AKIAU                │ Active   │ 2023-05-29 07:30:19 │            0 │
╘══════════════════════╧══════════╧═════════════════════╧══════════════╛
```

```bash
python3 iam.py password-reset --user vijay
```
```
Console password reset successfully.
╒════════════════════╤══════════════════╕
│ Field              │ Value            │
╞════════════════════╪══════════════════╡
│ Username           │ vijay            │
├────────────────────┼──────────────────┤
│ Temporary password │ 8eap.d!>j1~8.M9) │
╘════════════════════╧══════════════════╛
```
```bash
python3 iam.py remove-user-from-group --user vijay --groupname Admin
```
```
User 'vijay' removed from group 'Admin' successfully.
```

```bash
python3 iam.py remove-user-from-group --user vijay --groupname Admin
```
```
User 'vijay' removed from group 'Admin' successfully.
```
