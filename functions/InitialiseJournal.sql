--Run this script to initialise the journal database schema in Supabase
--https://supabase.com/

--Table to hold saved entries
create table entry (
  entryid bigserial primary key,
  entrydate date,
  entrytext text,
  sentiment decimal,
  mood text,
  weather text,
  temperature decimal,
  imagepath text,
  datecreated timestamptz,
  datemodified timestamptz,
  datedeleted timestamptz
);

--Table to hold step count data
create table step (
  stepid bigserial primary key,
  stepdate date,
  steps int,
  datecreated timestamptz,
  datemodified timestamptz,
  datedeleted timestamptz
);