DROP TABLE IF EXISTS emails;
DROP TABLE IF EXISTS phone_numbers;

create user replicator with replication encrypted password 'replicator_password';
select pg_create_physical_replication_slot('replication_slot');

CREATE TABLE emails (id int PRIMARY KEY, email VARCHAR(255));
CREATE TABLE phone_numbers (id int PRIMARY KEY, phone_number VARCHAR(255));
#INSERT INTO emails (id, email) values (1, 'sacho@ptsecurity.com'), (2, 'barama@ptsecurity.com');
#INSERT INTO phone_numbers (id, phone_number) values (1, '+79876543212'), (2, '+79865461231');
