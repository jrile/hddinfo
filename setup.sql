drop database if exists hdds;

create database hdds;

use hdds;

create table drive_group (id int not null auto_increment, /* describes a "group" of drives */
name varchar(50) not null,
notes text,
location varchar(50),
primary key(id));

create table drives (label varchar(20), 
location varchar(50), 
serial varchar(50) not null, 
notes text,
username varchar(20),
drive_group int default null, /* will be used to group drives together */
primary key (serial), 
foreign key (drive_group) references drive_group(id));

create table folders (folder_sequence int not null auto_increment, 
serial varchar(50) not null, 
folder_name varchar(50), 
primary key (folder_sequence),
foreign key (serial) references drives (serial));

create table files (file_sequence int not  null auto_increment,
name varchar(50), 
folder_sequence int not null, 
created datetime, 
notes text, 
primary key (file_sequence),
foreign key (folder_sequence) references folders (folder_sequence));

create table checkout (user_id int not null,
serial varchar(50) not null,
primary key (user_id, serial));


/* setting up some test values */
insert into drives (serial) values ('test');