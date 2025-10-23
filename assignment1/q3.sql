-- Create title table
CREATE TABLE title (
    WORKER_REF_ID INTEGER NOT NULL,
    WORKER_TITLE TEXT NOT NULL,
    AFFECTED_FROM TEXT NOT NULL,
    FOREIGN KEY (WORKER_REF_ID) REFERENCES worker(WORKER_ID)
);

-- Insert data into title table
INSERT INTO title (WORKER_REF_ID, WORKER_TITLE, AFFECTED_FROM) VALUES
(1, 'Manager', '2023-02-20 00:00:00'),
(2, 'Executive', '2023-06-11 00:00:00'),
(8, 'Executive', '2023-06-11 00:00:00'),
(5, 'Manager', '2023-06-11 00:00:00'),
(4, 'Asst. Manager', '2023-06-11 00:00:00'),
(7, 'Executive', '2023-06-11 00:00:00'),
(6, 'Lead', '2023-06-11 00:00:00'),
(3, 'Lead', '2023-06-11 00:00:00');