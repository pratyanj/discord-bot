-- CreateTable
CREATE TABLE "membercount" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "Total_Members" BIGINT NOT NULL,
    "Online_Members" BIGINT NOT NULL,
    "Bots" BIGINT NOT NULL
);
