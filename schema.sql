drop table if exists users;
CREATE TABLE users ( 
    username varchar(255) PRIMARY KEY, 
    password varchar(255), 
    salt varchar(255),
    email varchar(255), 
    role varchar(255))
