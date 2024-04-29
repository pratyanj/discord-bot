-- SERVERS --
CREATE TABLE IF NOT EXISTS `servers` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `server_name` text NOT NULL,
  `prefix` var NOT NULL,
  `log_channel` int(50) NOT NULL,
);

CREATE TABLE IF NOT EXISTS `STATUS`(
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `welcome` boolean NOT NULL,
  `JOIN_ROLE` boolean NOT NULL,
  `goodbye` boolean NOT NULL,
  `IMAGES_ONLY` boolean NOT NULL,
  `LINKS_ONLY` boolean NOT NULL,
  `REACTION_VERIFICATION_ROLE` boolean NOT NULL,
  `youtube_channel` boolean NOT NULL,
  
);
-- LEVEL --
CREATE TABLE IF NOT EXISTS `LEVEL_SETTING` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `level_up_channel_id` int(50) NOT NULL,
  `level_up_channel_name` text NOT NULL,
);

CREATE TABLE IF NOT EXISTS `No_xp_channel` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `channel_id` int(50) NOT NULL,
  `channel_name` text NOT NULL,
);

CREATE TABLE IF NOT EXISTS `No_xp_role` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `role_id` int(50) NOT NULL,
  `role_name` text NOT NULL,
);

CREATE TABLE IF NOT EXISTS `LEVEL_ROLE` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `level` int(1000) NOT NULL,
  `role_id` int(50) NOT NULL,
  `role_name` text NOT NULL,
  `level_up_message` text NOT NULL,
);

CREATE TABLE IF NOT EXISTS `users_Level` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `user_id` int(50) NOT NULL,
  `user_name` text NOT NULL,
  `level` int(1000) NOT NULL,
  `xp` int(100) NOT NULL,

);
-- WELCOME/GOODBYE SETTINGS --
CREATE TABLE IF NOT EXISTS `welcome` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `channel_id` int(50) NOT NULL,
  `channel_name` text NOT NULL,
  `message` text NOT NULL,
);

CREATE TABLE IF NOT EXISTS `goodbye` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `channel_id` int(50) NOT NULL,
  `channel_name` text NOT NULL,
  `message` text NOT NULL,
);

-- feature --
CREATE TABLE IF NOT EXISTS `JOIN_ROLE` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `role_id` int(50) NOT NULL,
  `role_name` text NOT NULL,
);

CREATE TABLE IF NOT EXISTS `REACTION_VERIFICATION_ROLE` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `role_id` int(50) NOT NULL,
  `role_name` text NOT NULL,
  `reaction` text NOT NULL,
  `channel_id` int(50) NOT NULL,
  `channel_name` text NOT NULL,
  `dm_message` text NOT NULL,
);

CREATE TABLE IF NOT EXISTS `IMAGES_ONLY` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `channel_id` int(50) NOT NULL,
  `channel_name` text NOT NULL,
);
CREATE TABLE IF NOT EXISTS `LINKS_ONLY` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `channel_id` int(50) NOT NULL,
  `channel_name` text NOT NULL,
 );


-- YOUTUBE --
CREATE TABLE if not exists `youtube_setting` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `channel_id` int(50) NOT NULL,
  `channel_name` text NOT NULL,
);

CREATE TABLE if not exists `youtube_sub_channel` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `channel` text NOT NULL,
);

CREATE TABLE if not exists `youtube_videos` (
  `ID` INT NOT NULL PRIMARY KEY,
  `server_id` int(50) NOT NULL,
  `channel` text NOT NULL,
  `video_id` text NOT NULL,
);


-- MODARATION SETTINGS--
CREATE TABLE IF NOT EXISTS `warns` (
  `ID` INT NOT NULL PRIMARY KEY,
  `user_id` text(20) NOT NULL,
  `server_id` text(20) NOT NULL,
  `moderator_id` text(20) NOT NULL,
  `reason` text NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
