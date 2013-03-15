/*--create profile/tags association table*/
CREATE TABLE `t_profile_tags` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `profile_id` integer NOT NULL,
    `tag_id` integer NOT NULL,
    UNIQUE (`profile_id`, `tag_id`)
);

/*--create FK constraint for table t_profile_tags */
ALTER TABLE `t_profile_tags` ADD CONSTRAINT `profile_id_refs_id_2ea86c16` FOREIGN KEY (`profile_id`) REFERENCES `t_profile` (`id`);

ALTER TABLE `t_profile_tags` ADD CONSTRAINT `tag_id_refs_id_5cd7d4fb` FOREIGN KEY (`tag_id`) REFERENCES `t_tag` (`id`);

/*--website添加个性域名*/
ALTER TABLE t_profile ADD COLUMN website varchar(40);

/*--标签label属性,用于显示*/
ALTER TABLE t_tag ADD COLUMN label varchar(50) NOT NULL;

/*--添加地理坐标*/
alter table t_activity add column coordinates varchar(30);

/*--活动海报*/
alter table t_activity drop column poster_pic;
alter table t_activity add column `big_poster` varchar(80);
alter table t_activity add column `normal_poster` varchar(80);
alter table t_activity add column `small_poster` varchar(80);
alter table t_activity add column `tmp_poster` varchar(80);

/*--用户头像*/
alter table t_profile drop column pic;
alter table t_profile drop column tmp_pic;
alter table t_profile add column `big_pic` varchar(80);
alter table t_profile add column `normal_pic` varchar(80);
alter table t_profile add column `small_pic` varchar(80);
alter table t_profile add column `tmp_pic` varchar(80);

alter table t_activity drop column category;
alter table t_activity add column `category` smallint NOT NULL;

/*--活动创建时是否存为草稿 */
alter table t_activity add column `is_draft` bool NOT NULL;
alter table t_activity add column `area_id` integer NOT NULL;

alter table t_activity add column `is_audited` bool NOT NULL;

commit;
