-- drop table if exists entries;
-- 用户发表内容
create table entries (
    id integer primary key autoincrement,
    -- 用户id
    uid integer not null,
    -- 发表时间
    create_time TIMESTAMP default CURRENT_TIMESTAMP,
    -- 标题
    title string not null,
    -- 内容
    text string not null
);

-- drop table if exists user;
-- 用户表
create table userinfo (
    id integer primary key autoincrement,
    -- 用户
    username string not null,
    -- 密码
    password string not null,
    -- 用户是否删除
    isdel tinyint DEFAULT 0
)