# Database
QuestDB database, set ip & port in config.py on sensor (default works on port 9000)

https://questdb.com/docs/quick-start/

## Database schema
- `config`
    - Columns:
    - `id` - sensor id `[int]`
    - `lat` - sensor latitude `[double]`
    - `lon` - sensor longitude `[double]`
    - `location` - sensor location, e.g. name of place or street `[string]`
    - `description` - more detalied info about sensor `[string]`
- `sensors`
    - Columns:
    - `timestamp`
    - `id` - sensor id corresponding with `id` from `config` table `[int]`
    - `temperature` `[double]`
    -  `humidity` `[double]`
    - `pm1` `[int]`
    - `pm25` `[int]`
    - `pm10` `[int]`
- `log` (work in progress)
    - Columns:
    - `id` `[int]`
    - `timestamp`
    - `code` - log message type, e.g. 0 - info, 1 - warning, 2 - error `[int]`
    - `message` - more detailed information `[string]`

## Quick configuration
Paste code from `configuration.sql` into QuestDB console to quickly create needed tables.

## Config example

```sql
INSERT INTO config (id, lat, lon, location, description) VALUES (0, 50.581867, 16.690958, 'Pracownia', 'Czujnik 1 w pracowni')
```