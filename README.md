# usable-itdk
Parse CAIDA ITDK files into a database

## Files
### properties.py
Utility functions for deserializing JSON files and unfolding the resulting dictionaries

#### properties/db.json
Metadata for the target database

* driver
  * type: string
  * defines the driver to use
  * when using SQLite, only must write "SQLite3" in this field, all other fields in db.json can be left blank

* server
  * type: string
  * server where target database is located
  * unused for SQLite
  * needed for connection string for other DB platforms

* name
  * type: string
  * database name
  * unused for SQLite
  * needed for connection string for other DB platforms

* user
  * type: string
  * database username for authentication
  * unused for SQLite
  * needed for connection string for other DB platforms

* pwd
  * type: string
  * password for database user given in property "user"
  * unused for SQLite
  * needed for connection string for other DB platforms

#### properties/itdk_version.json
Metadata for the target ITDK edition

* ip_version
  * type: integer
  * value can be either 4 or 6
  * required

* year
  * type: integer
  * example value: 2020
  * required

* month
  * type: integer
  * example value: 4
    * the JSON parser gets angry when you try to put leading zeros on integers
    * i definitely could just make this a string but i don't want to confuse people about the formatting, keeping it simple and converting it in the code
  * required

* day
* type: integer
* example value: 9
  * the JSON parser gets angry when you try to put leading zeros on integers
  * i definitely could just make this a string but i don't want to confuse people about the formatting, keeping it simple and converting it in the code
* required

* url
  * type: string
  * URL of dataset files, excluding the segments specific to edition date, topology choice, specific file, etc
  * example value: "http://publicdata.caida.org/datasets/topology/ark/ipv4/itdk/"

* topo_choice
  * type: string
  * example values
    * "midar-iff"
    * "kapar-midar-iff"
  * necessary for building wget URLs, file names, etc.

* compression_extension
  * type: string
  * example value: ".bz2"
  * included this because i'm not sure about the compression type consistency throughout the archives

#### properties/os_env.json
Metadata for the OS environment hosting this suite

* os
  * type: string
  * example value: "Ubuntu"
  * identifying the OS where this suite is being run (I could figure this out programmatically probably but i can iterate on that later)
  * i think the os property will only be important if we want to make this suite work on Windows too

* username
  * type: string
  * OS user running this suite
  * $HOME for this user is generated and prepended to the ITDK file location

### log_util.py
Functions to generate a timestamp for the current run's logs, and to pull STDOUT, STDERR, and return code for a given command

### parse_util.py
Defines regex for ITDK nodes and links, IP addresses (v4 or v6), etc.

### download.py

### decompress.py

### initialize_db.py
Functions for initializing a connection to the target DB and creating the schema

### read_in_nodes.py
Parses ITDK .nodes file and INSERTs each entry to map_address_to_node

### read_in_links.py
Parses ITDK .links file and INSERTs each entry to map_link_to_nodes
