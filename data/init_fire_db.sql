-- ----------------
-- for fire alarms
-- ----------------
CREATE DATABASE daeduck_alarm_momoda;

CREATE TABLE IF NOT EXISTS fire_alarms (
    id MEDIUMINT NOT NULL AUTO_INCREMENT,
    occurrences varchar(64),
    sensor varchar(64),
    status varchar(64),
    primary key (id)
);

insert into fire_alarms (occurrences, sensor, status) values ('2017-11-09 05:31:38', 'F101141', 'fire');

insert into fire_alarms (occurrences, sensor, status) values ('2017-11-09 05:31:38', 'F101141', 'recovery');

insert into fire_alarms (occurrences, sensor, status) values ('2017-11-09 05:31:38', 'F101111', 'fire');

insert into fire_alarms (occurrences, sensor, status) values ('2017-11-09 05:31:38', 'F101111', 'recovery');

insert into fire_alarms (occurrences, sensor, status) values ('2017-11-09 05:31:38', 'F000000', 'recovery');

insert into fire_alarms (occurrences, sensor, status) values ('2017-11-09 05:31:38', 'F', 'recovery');


-- -------
-- for gas alarms
-- -------
