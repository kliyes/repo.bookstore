
/* 活动标签表 */
CREATE TABLE `t_activitytag` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(40) NOT NULL,
    `label` varchar(50) NOT NULL
);

/* 活动与标签关联表 */
CREATE TABLE `t_activity_tags` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `activity_id` integer NOT NULL,
    `activitytag_id` integer NOT NULL,
    UNIQUE (`activity_id`, `activitytag_id`)
);

/* 邮件发送次数记录表 */
CREATE TABLE `t_email_sent_count` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `email_address` varchar(75) NOT NULL,
    `signup_count` integer NOT NULL,
    `reset_pwd_count` integer NOT NULL
)
;

ALTER TABLE `t_activity_tags` ADD CONSTRAINT `activitytag_id_refs_id_1c3ae46b` FOREIGN KEY (`activitytag_id`) REFERENCES `t_activitytag` (`id`);

ALTER TABLE `t_activity` ADD CONSTRAINT `area_id_refs_id_104e7993` FOREIGN KEY (`area_id`) REFERENCES `t_area` (`id`);

/*--活动创建时是否存为草稿 */
alter table t_activity add column `is_draft` bool NOT NULL;
alter table t_activity add column `area_id` integer;
alter table t_activity add column `is_audited` bool NOT NULL;

alter table t_activitytag add column type integer NOT NULL;
alter table t_tag add column type integer NOT NULL;

/*--个人主页名 */
alter table t_profile add column `spacename` varchar(50);

/*--主办方名称 */
alter table t_activity add column `organizer` varchar(200);

/* 被回复的评论id,当某条评论为回复时,该字段不空 */
alter table t_comment add column `dest_comment_id` integer;

commit;
