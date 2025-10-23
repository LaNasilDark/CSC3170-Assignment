-- database: :memory:
-- Create worker table
CREATE TABLE
    worker (
        WORKER_ID INTEGER PRIMARY KEY,
        FIRST_NAME TEXT NOT NULL,
        LAST_NAME TEXT NOT NULL,
        SALARY INTEGER NOT NULL,
        JOINING_DATE TEXT NOT NULL,
        DEPARTMENT TEXT NOT NULL
    );

-- Insert data into worker table
INSERT INTO
    worker (
        WORKER_ID,
        FIRST_NAME,
        LAST_NAME,
        SALARY,
        JOINING_DATE,
        DEPARTMENT
    )
VALUES
    (
        1,
        'Monika',
        'Arora',
        100000,
        '21-02-20 09.00.00',
        'HR'
    ),
    (
        2,
        'Niharika',
        'Verma',
        80000,
        '21-06-11 09.00.00',
        'Admin'
    ),
    (
        3,
        'Vishal',
        'Singhal',
        300000,
        '21-02-20 09.00.00',
        'HR'
    ),
    (
        4,
        'Amitabh',
        'Singh',
        500000,
        '21-02-20 09.00.00',
        'Admin'
    ),
    (
        5,
        'Vivek',
        'Bhati',
        500000,
        '21-06-11 09.00.00',
        'Admin'
    ),
    (
        6,
        'Vipul',
        'Diwan',
        200000,
        '21-06-11 09.00.00',
        'Account'
    ),
    (
        7,
        'Satish',
        'Kumar',
        75000,
        '21-01-20 09.00.00',
        'Account'
    ),
    (
        8,
        'Geetika',
        'Chauhan',
        90000,
        '21-04-11 09.00.00',
        'Admin'
    );

CREATE TABLE
    bonus (
        WORKER_REF_ID INTEGER NOT NULL,
        BONUS_DATE TEXT NOT NULL,
        BONUS_AMOUNT INTEGER NOT NULL,
        FOREIGN KEY (WORKER_REF_ID) REFERENCES worker (WORKER_ID)
    );

-- Insert data into bonus table
INSERT INTO
    bonus (WORKER_REF_ID, BONUS_DATE, BONUS_AMOUNT)
VALUES
    (1, '23-02-20', 5000),
    (2, '23-06-11', 3000),
    (3, '23-02-20', 4000),
    (1, '23-02-20', 4500),
    (2, '23-06-11', 3500);

-- Create title table
CREATE TABLE
    title (
        WORKER_REF_ID INTEGER NOT NULL,
        WORKER_TITLE TEXT NOT NULL,
        AFFECTED_FROM TEXT NOT NULL,
        FOREIGN KEY (WORKER_REF_ID) REFERENCES worker (WORKER_ID)
    );

-- Insert data into title table
INSERT INTO
    title (WORKER_REF_ID, WORKER_TITLE, AFFECTED_FROM)
VALUES
    (1, 'Manager', '2023-02-20 00:00:00'),
    (2, 'Executive', '2023-06-11 00:00:00'),
    (8, 'Executive', '2023-06-11 00:00:00'),
    (5, 'Manager', '2023-06-11 00:00:00'),
    (4, 'Asst. Manager', '2023-06-11 00:00:00'),
    (7, 'Executive', '2023-06-11 00:00:00'),
    (6, 'Lead', '2023-06-11 00:00:00'),
    (3, 'Lead', '2023-06-11 00:00:00');

SELECT
    DEPARTMENT,
    FIRST_NAME,
    SALARY
FROM
    (
        SELECT
            DEPARTMENT,
            FIRST_NAME,
            SALARY,
            ROW_NUMBER() OVER (
                PARTITION BY
                    DEPARTMENT
                ORDER BY
                    SALARY ASC
            ) as rn
        FROM
            worker
    ) ranked
WHERE
    rn = 1
ORDER BY
    DEPARTMENT DESC;
