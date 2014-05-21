delete from drives;
delete from folders;
delete from files;
alter table folders auto_increment=1;
alter table files auto_increment=1;