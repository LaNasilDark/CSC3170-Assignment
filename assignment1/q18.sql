-- Question 18: Write an SQL query to print the names of workers having the lowest salary in each department.

-- Method 1: Using window function with ROW_NUMBER()
SELECT DEPARTMENT, FIRST_NAME, SALARY
FROM (
    SELECT DEPARTMENT, FIRST_NAME, SALARY,
           ROW_NUMBER() OVER (PARTITION BY DEPARTMENT ORDER BY SALARY ASC) as rn
    FROM worker
) ranked
WHERE rn = 1
ORDER BY DEPARTMENT;

-- Method 2: Using correlated subquery (alternative approach)
-- SELECT w.DEPARTMENT, w.FIRST_NAME, w.SALARY
-- FROM worker w
-- WHERE w.SALARY = (
--     SELECT MIN(w2.SALARY)
--     FROM worker w2
--     WHERE w2.DEPARTMENT = w.DEPARTMENT
-- )
-- ORDER BY w.DEPARTMENT;

-- Expected Output:
-- DEPARTMENT|FIRST_NAME|SALARY
-- HR|Monika|100000
-- Admin|Niharika|80000
-- Account|Satish|75000