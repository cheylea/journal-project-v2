--Run this script to initialise the journal database schema in Supabase

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

create table step (
  stepid bigserial primary key,
  stepdate date,
  steps int,
  datecreated timestamptz,
  datemodified timestamptz,
  datedeleted timestamptz
);