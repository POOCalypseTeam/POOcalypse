# Structure base de données

Tous les mondes sont stockées dans la même base de données, `mondes.db`

Une première table stocke les différents mondes:

```SQL
CREATE TABLE worlds (
    id INTEGER PRIMARY KEY,
    name TEXT,
);
```
