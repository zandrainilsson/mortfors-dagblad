\set ON_ERROR_STOP on
revoke all privileges on database ai7773_dagbladm from public;
drop table if exists Publicering;
drop table if exists Journalist;
drop table if exists Kommentar;
drop table if exists Bild_Artikel;
drop table if exists Artikel;
drop table if exists Underkategori;
drop table if exists Huvudkategori;
drop table if exists Bild;

create table Bild
(BildID         SERIAL UNIQUE,
Filnamn         VARCHAR(60),
AltText         VARCHAR(30),
primary key (BildID));

create table Huvudkategori
(HID            SERIAL UNIQUE,
Huvudkategori   VARCHAR(30),
primary key (HID));

create table Underkategori
(UndID          SERIAL UNIQUE,
Underkategori   VARCHAR(30),
HID             INT,
primary key (UndID),
foreign key (HID) references Huvudkategori(HID));

create table Artikel
(ArtikelID      SERIAL UNIQUE,
Titel           VARCHAR(200),
Ingress         VARCHAR(200),
Artikel         text,
Datum           DATE,
UndID           INT,
primary key (ArtikelID),
foreign key (UndID) references Underkategori(UndID));

create table Bild_Artikel
(ArtikelID      int,
BildID          int,
Bild_Text       VARCHAR(150),
primary key (BildID, ArtikelID),
foreign key (BildID) references Bild(BildID),
foreign key (ArtikelID) references Artikel(ArtikelID));


create table Kommentar
(ID             SERIAL UNIQUE,
Signatur        VARCHAR(80),
Kommentar       VARCHAR(500),
Datum           DATE,
Tid             TIME,
ArtikelID       int,
primary key (ID, ArtikelID),
foreign key (ArtikelID) references Artikel(ArtikelID));

create table Journalist
(PersonNR       varchar(12),
Namn            VARCHAR(60),
Anteckningar    VARCHAR(100),
primary key (PersonNR));

create table Publicering
(ArtikelID      int,
PersonNR        varchar(12),
primary key (ArtikelID, PersonNR),
foreign key (ArtikelID) references Artikel(ArtikelID),
foreign key (PersonNr) references Journalist(PersonNR));