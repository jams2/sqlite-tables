BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "test_table" (
	"firstname"	TEXT,
	"lastname"	TEXT
);
COMMIT;
