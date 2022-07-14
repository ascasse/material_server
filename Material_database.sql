BEGIN TRANSACTION;

DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Items;

CREATE TABLE "Items"
(
	"Id" INTEGER NOT NULL,
	"Text" TEXT NOT NULL,
	"LastUse" TEXT,
	"Views" INTEGER DEFAULT 0,
	"Image" TEXT,
	"CategoryId" INTEGER,
	FOREIGN KEY("CategoryId") REFERENCES Categories("Id"),
	PRIMARY KEY("Id")
);

CREATE TABLE "Categories"
(
	"Id" INTEGER NOT NULL,
	"Name" TEXT UNIQUE NOT NULL,
	"LastUse" TEXT DEFAULT NULL,
	PRIMARY KEY("Id")
);

COMMIT;
