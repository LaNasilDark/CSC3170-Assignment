1. students (学生表)

student_id (PK)
password
name
gender
school
dorm_id (FK)
2. dormitories (宿舍表)

dorm_id (PK)
building_no
floor_no
room_no
total_beds
occupied_beds
3. dorm_change_requests (调换申请表)

request_id (PK)
student_id (FK)
current_dorm_id (FK)
target_dorm_id (FK)
reason
status (pending/approved/rejected)
request_time
process_time
4. maintenance_requests (维修申请表)

maintenance_id (PK)
student_id (FK)
dorm_id (FK)
description
status (pending/processing/completed)
submit_time
complete_time
5. bills (账单表)

bill_id (PK)
dorm_id (FK)
electricity_fee
water_fee
billing_month
status (unpaid/paid)
6. administrators (管理员表)

admin_id (PK)
username
password
name
phone
