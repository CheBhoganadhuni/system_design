create user 'auth_user'@'localhost' identified by 'Auth123';
create database if not exists auth;
grant all privileges on auth.* to 'auth_user'@'localhost';

use auth;
create table user (
    id int not null auto_increment primary key,
    email varchar(255) not null unique,
    password varchar(255) not null
);

insert into user (email, password) values ('che@gmail.com', 'Admin123');
