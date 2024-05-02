-- CreateTable
CREATE TABLE "Server" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "server_name" TEXT NOT NULL,
    "prefix" TEXT NOT NULL,
    "log_channel" BIGINT NOT NULL
);

-- CreateTable
CREATE TABLE "Status" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "welcome" BOOLEAN NOT NULL DEFAULT false,
    "JOIN_ROLE" BOOLEAN NOT NULL DEFAULT false,
    "goodbye" BOOLEAN NOT NULL DEFAULT false,
    "IMAGES_ONLY" BOOLEAN NOT NULL DEFAULT false,
    "LINKS_ONLY" BOOLEAN NOT NULL DEFAULT false,
    "REACTION_VERIFICATION_ROLE" BOOLEAN NOT NULL DEFAULT false,
    "youtube_channel" BOOLEAN NOT NULL DEFAULT false
);

-- CreateTable
CREATE TABLE "Welcome" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "status" BOOLEAN NOT NULL DEFAULT false,
    "channel_id" BIGINT NOT NULL,
    "channel_name" TEXT NOT NULL,
    "message" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "Goodbye" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "status" BOOLEAN NOT NULL DEFAULT false,
    "channel_id" BIGINT NOT NULL,
    "channel_name" TEXT NOT NULL,
    "message" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "JoinRole" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "status" BOOLEAN NOT NULL DEFAULT false,
    "server_id" BIGINT NOT NULL,
    "role_id" BIGINT NOT NULL,
    "role_name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "YouTubeSetting" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "status" BOOLEAN NOT NULL DEFAULT false,
    "channel_id" BIGINT NOT NULL,
    "channel_name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "ReactionVerificationRole" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "role_id" BIGINT NOT NULL,
    "role_name" TEXT NOT NULL,
    "reaction" TEXT NOT NULL,
    "channel_id" BIGINT NOT NULL,
    "channel_name" TEXT NOT NULL,
    "status" BOOLEAN NOT NULL DEFAULT false,
    "dm_message" BOOLEAN NOT NULL DEFAULT false
);

-- CreateTable
CREATE TABLE "LevelSetting" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "status" BOOLEAN NOT NULL DEFAULT false,
    "level_up_channel_id" BIGINT NOT NULL,
    "level_up_channel_name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "NoXPChannel" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "channel_id" BIGINT NOT NULL,
    "channel_name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "NoXPRole" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "role_id" BIGINT NOT NULL,
    "role_name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "LevelRole" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "level" INTEGER NOT NULL,
    "role_id" BIGINT NOT NULL,
    "role_name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "UsersLevel" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "user_id" BIGINT NOT NULL,
    "user_name" TEXT NOT NULL,
    "level" INTEGER NOT NULL DEFAULT 0,
    "xp" INTEGER NOT NULL DEFAULT 0
);

-- CreateTable
CREATE TABLE "ImagesOnly" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "channel_id" BIGINT NOT NULL,
    "channel_name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "LinksOnly" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "channel_id" BIGINT NOT NULL,
    "channel_name" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "YouTubeSubChannel" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "channel" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "YouTubeVideos" (
    "ID" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "server_id" BIGINT NOT NULL,
    "channel" TEXT NOT NULL,
    "video_id" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "Server_server_id_key" ON "Server"("server_id");

-- CreateIndex
CREATE UNIQUE INDEX "Status_server_id_key" ON "Status"("server_id");

-- CreateIndex
CREATE UNIQUE INDEX "Welcome_server_id_key" ON "Welcome"("server_id");

-- CreateIndex
CREATE UNIQUE INDEX "Goodbye_server_id_key" ON "Goodbye"("server_id");

-- CreateIndex
CREATE UNIQUE INDEX "JoinRole_server_id_key" ON "JoinRole"("server_id");

-- CreateIndex
CREATE UNIQUE INDEX "YouTubeSetting_server_id_key" ON "YouTubeSetting"("server_id");

-- CreateIndex
CREATE UNIQUE INDEX "ReactionVerificationRole_server_id_key" ON "ReactionVerificationRole"("server_id");

-- CreateIndex
CREATE UNIQUE INDEX "LevelSetting_server_id_key" ON "LevelSetting"("server_id");
