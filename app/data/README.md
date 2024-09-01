# How to Get Data

This project uses the AdventureWorks2022 (OLTP) and AdventureWorksDW2022 (Data Warehouse) databases for testing and development purposes. To set up your environment, you’ll need to restore these databases from the provided backup files.

## Prerequisites

- [AdventureWorks2022.bak]( https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorks2022.bak)
- [AdventureWorksDW2022.bak](https://github.com/Microsoft/sql-server-samples/releases/download/adventureworks/AdventureWorksDW2022.bak)

## Restoring the Databases

1. Place the Backup Files:
    - After downloading, place the .bak files in the app/data folder of this project.
2. Start the SQL Server Container:
    - Build and start your container by running `docker-compose up` in the project root.
3. Restore the Databases:
    - Once the container is running, execute the following SQL script to restore both databases:

```sql
-- Restore AdventureWorks OLTP
RESTORE DATABASE [AdventureWorks2022]
FROM DISK = N'/var/opt/mssql/backup/AdventureWorks2022.bak'
WITH MOVE 'AdventureWorks2022' TO '/var/opt/mssql/data/AdventureWorks2022.mdf',
     MOVE 'AdventureWorks2022_log' TO '/var/opt/mssql/data/AdventureWorks2022_log.ldf',
     REPLACE;

-- Restore AdventureWorks DW
RESTORE DATABASE [AdventureWorksDW2022]
FROM DISK = N'/var/opt/mssql/backup/AdventureWorksDW2022.bak'
WITH MOVE 'AdventureWorksDW2022' TO '/var/opt/mssql/data/AdventureWorksDW2022.mdf',
     MOVE 'AdventureWorksDW2022_log' TO '/var/opt/mssql/data/AdventureWorksDW2022_log.ldf',
     REPLACE;
```
