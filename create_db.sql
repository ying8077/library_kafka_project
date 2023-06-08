CREATE TABLE books (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `ISBN` TEXT,
    `title` TEXT,
    `author` TEXT,
    `category` TEXT,
    `version` TEXT,
    `publisher` TEXT,
    `img` TEXT,
    `description` TEXT
);

CREATE TABLE recommends (
    `ISBN` INTEGER PRIMARY KEY,
    `title` TEXT,
    `author` TEXT,
    `category` TEXT,
    `version` TEXT
);

CREATE TABLE readers (
    `rname` TEXT,
    `ssn` TEXT PRIMARY KEY,
    `address` TEXT,
    `mail` TEXT,
    `phone` TEXT,
    `password` password
);

CREATE TABLE staffs (
    `sname` TEXT,
    `empid` TEXT PRIMARY KEY,
    `password` TEXT
);

CREATE TABLE publishers (
    `publisher_id` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    `pname` TEXT,
    FOREIGN KEY(`pname`) REFERENCES `books`(`publisher`) ON DELETE CASCADE
);

CREATE TABLE reports (
    `Reg_no` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    `User_id` TEXT,
    `book_no` TEXT,
    `title` TEXT,
    `issue` DATETIME DEFAULT (datetime('now', 'localtime')),
    `return_date` DATETIME DEFAULT (datetime('now', 'localtime', '+30 days')),
    FOREIGN KEY(`User_id`) REFERENCES `readers`(`ssn`) ON DELETE CASCADE,
    FOREIGN KEY(`book_no`) REFERENCES `books`(`ISBN`) ON DELETE CASCADE
    FOREIGN KEY(`title`) REFERENCES `books`(`title`) ON DELETE CASCADE
);

CREATE TABLE borrowtopic (
    `No` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    `user_ssn` TEXT,
    `user_name` TEXT,
    `behavior` TEXT,
    `book_name` TEXT
);

CREATE TABLE logintopic (
    `No` INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    `user_ssn` TEXT,
    `user_name` TEXT,
    `behavior` TEXT
);