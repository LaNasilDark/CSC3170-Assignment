import pymysql
import sys
import io
from pathlib import Path

# 设置UTF-8编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("="*80)
print("🗄️  创建数据库并导入表结构和数据")
print("="*80)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # 请输入你的MySQL密码
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_password():
    """获取MySQL密码"""
    import getpass
    password = getpass.getpass("请输入MySQL root密码: ")
    return password

def execute_sql_file(connection, sql_file_path, db_name=None):
    """执行SQL文件"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 分割SQL语句（按分号分割，但要处理存储过程等特殊情况）
    statements = []
    current_statement = []
    in_delimiter = False
    
    for line in sql_content.split('\n'):
        line = line.strip()
        
        # 跳过注释和空行
        if not line or line.startswith('--'):
            continue
            
        # 检查是否是DELIMITER语句
        if line.upper().startswith('DELIMITER'):
            in_delimiter = not in_delimiter
            continue
        
        current_statement.append(line)
        
        # 检查语句结束
        if not in_delimiter and line.endswith(';'):
            statement = ' '.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []
    
    # 添加最后一个语句（如果有）
    if current_statement:
        statement = ' '.join(current_statement)
        if statement.strip():
            statements.append(statement)
    
    # 执行SQL语句
    with connection.cursor() as cursor:
        if db_name:
            cursor.execute(f"USE {db_name}")
        
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(statements, 1):
            try:
                # 跳过一些特殊语句
                statement_upper = statement.upper().strip()
                if (statement_upper.startswith('USE ') or 
                    statement_upper.startswith('SET ') or
                    statement_upper.startswith('DROP DATABASE')):
                    cursor.execute(statement)
                    success_count += 1
                elif statement_upper.startswith('CREATE OR REPLACE VIEW'):
                    # 处理视图创建
                    cursor.execute(statement)
                    success_count += 1
                elif statement.strip():
                    cursor.execute(statement)
                    success_count += 1
                    
                    # 每100条显示进度
                    if success_count % 100 == 0:
                        print(f"  已执行 {success_count} 条语句...")
                        
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # 只显示前5个错误
                    print(f"  ⚠️  语句 {i} 执行失败: {str(e)[:100]}")
        
        connection.commit()
        return success_count, error_count

try:
    print("\n步骤 1: 连接到MySQL服务器...")
    
    # 获取密码
    DB_CONFIG['password'] = get_password()
    
    # 连接到MySQL（不指定数据库）
    connection = pymysql.connect(**DB_CONFIG)
    print("✅ 连接成功!")
    
    # 创建数据库
    print("\n步骤 2: 创建数据库...")
    with connection.cursor() as cursor:
        cursor.execute("DROP DATABASE IF EXISTS dormitory_management_system")
        cursor.execute("""
            CREATE DATABASE dormitory_management_system 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_unicode_ci
        """)
    connection.commit()
    print("✅ 数据库 'dormitory_management_system' 创建成功!")
    
    # 执行表创建脚本
    print("\n步骤 3: 创建数据库表...")
    sql_dir = Path(r"f:\OneDrive_Files\OneDrive - CUHK-Shenzhen\onedrive_container\TASKS\USING_Term3.1\CSC3170\project\sql")
    create_tables_file = sql_dir / "01_create_tables.sql"
    
    if not create_tables_file.exists():
        print(f"❌ 文件不存在: {create_tables_file}")
        sys.exit(1)
    
    success, errors = execute_sql_file(connection, create_tables_file, 'dormitory_management_system')
    print(f"✅ 表结构创建完成! (成功: {success}, 错误: {errors})")
    
    # 验证表创建
    with connection.cursor() as cursor:
        cursor.execute("USE dormitory_management_system")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n已创建的表:")
        for table in tables:
            table_name = list(table.values())[0]
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"  - {table_name} (记录数: {count})")
    
    # 导入数据
    print("\n步骤 4: 导入测试数据...")
    print("⚠️  这可能需要几分钟，请耐心等待...")
    
    insert_data_file = sql_dir / "02_insert_data.sql"
    
    if not insert_data_file.exists():
        print(f"❌ 文件不存在: {insert_data_file}")
    else:
        success, errors = execute_sql_file(connection, insert_data_file, 'dormitory_management_system')
        print(f"✅ 数据导入完成! (成功: {success}, 错误: {errors})")
    
    # 验证数据导入
    print("\n步骤 5: 验证数据导入...")
    with connection.cursor() as cursor:
        cursor.execute("USE dormitory_management_system")
        
        tables_to_check = [
            'administrators',
            'dormitories', 
            'students',
            'dorm_change_requests',
            'maintenance_requests',
            'bills'
        ]
        
        print("\n数据统计:")
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"  {table:30s}: {count:>6,} 条")
    
    print("\n" + "="*80)
    print("🎉 数据库创建和数据导入完成!")
    print("="*80)
    print("\n数据库信息:")
    print(f"  数据库名: dormitory_management_system")
    print(f"  字符集: utf8mb4")
    print(f"  主机: localhost")
    print(f"\n测试账号:")
    print(f"  管理员: admin / admin123")
    print(f"  学生: 121090001 / 123456 (任意学号)")
    
except pymysql.Error as e:
    print(f"\n❌ MySQL错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("\n数据库连接已关闭")
