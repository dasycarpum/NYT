/*
Created on 2023-06-04

@author: Roland

@abstract: The code creates 3 tables for 'nyt' database. The relationships between the tables in the database schema are as follows:

    book <-> review:
        One-to-Many Relationship: One book can have multiple reviews. The id_book column in the review table creates a foreign key relationship to the id column in the book table. So each row in the review table is associated with a row in the book table.

    book <-> rank:
        One-to-Many Relationship: One book can have multiple rankings (possibly in different categories or at different dates). The id_book column in the rank table creates a foreign key relationship to the id column in the book table. So each row in the rank table is associated with a row in the book table.

*/

CREATE TABLE book (
    id INT PRIMARY KEY,
    data JSONB NOT NULL
);


CREATE TABLE review (
    id_book INT NOT NULL REFERENCES book(id),
    id_review INT NOT NULL,
    stars INT,
    title TEXT,
    text TEXT,
    date DATE,
    PRIMARY KEY (id_book, id_review)
);


CREATE TABLE rank (
    id_book INT NOT NULL REFERENCES book(id),
    date Date NOT NULL,
    category VARCHAR(50) NOT NULL,
    rank INT,
    rank_last_week INT,
    weeks_on_list INT,
    PRIMARY KEY (id_book, date, category)
);
