# usable-itdk
Parse CAIDA ITDK files into a database

## Requirements

### pyodbc
Python package for communicating with databases
[PyPI Page](https://pypi.org/project/pyodbc/)
[Installation](https://github.com/mkleehammer/pyodbc/wiki/Install)

### SQLite 
```
sudo apt install libsqliteodbc
```

## Files
### properties.py

#### Deserializing JSON Files
* deserialize_os_env(file="properties/os_env.json")

* deserialize_itdk_version(file="properties/itdk_version.json")

* deserialize_db(file="properties/db.json")

#### Wrapper Functions to Extract Properties

##### os_env
* os_env__os(os_env)

* os_env__username(os_env)

* os_env__home(os_env)
** Get the full $HOME path for the username given
** Yields string

##### itdk_version
* itdk_version__ip_version(itdk_version)

* itdk_version__year(itdk_version)

* itdk_version__month(itdk_version)

* itdk_version__day(itdk_version)

* itdk_version__url(itdk_version)

* itdk_version__topo_choice(itdk_version)

* itdk_version__compression_extension(itdk_version)

* itdk_version__file_location(itdk_version)

* itdk_version__download(itdk_version)

* itdk_version__decompress(itdk_version)

##### db
* db__driver(db)

* db__server(db)

* db__name(db)

* db__user(db)

* db__pwd(db)

#### properties/db.json

* driver
** type: string

* server
** type: string

* name
** type: string

* user
** type: string

* pwd
** type: string

#### properties/itdk_version.json

* ip_version

* year

* month

* day

* url
** type: string

* topo_choice
** type: string

* compression_extension
** type: string

#### properties/os_env.json

* os
** type: string

* username
** type: string

### log_util.py

### parse_util.py

### download.py

### decompress.py

### initialize_db.py

### read_in_nodes.py

### read_in_links.py
