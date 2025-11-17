"""
更新.env文件中的数据库密码
"""
import getpass
import os

def update_env_password():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    # 读取当前.env文件
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 获取MySQL密码
    print("请输入MySQL root用户的密码:")
    password = getpass.getpass()
    
    # 更新DATABASE_URL行
    new_lines = []
    for line in lines:
        if line.startswith('DATABASE_URL='):
            new_line = f'DATABASE_URL=mysql+pymysql://root:{password}@localhost:3306/dormitory_management_system\n'
            new_lines.append(new_line)
            print(f"✅ 已更新数据库连接配置")
        else:
            new_lines.append(line)
    
    # 写回.env文件
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ .env文件已更新!")
    print(f"📂 文件路径: {env_path}")
    print("\n请重启后端服务器以使配置生效")

if __name__ == '__main__':
    update_env_password()
