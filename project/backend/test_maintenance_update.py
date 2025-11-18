"""
测试维修申请修改功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_update_maintenance():
    print("=" * 70)
    print("测试学生修改维修申请功能")
    print("=" * 70)
    
    # 1. 学生登录
    print("\n1. 学生登录...")
    login_data = {
        "username": "121090001",
        "password": "123456"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ 登录失败: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ 登录成功,Token: {token[:20]}...")
    
    # 2. 查看现有的维修申请
    print("\n2. 查看现有维修申请...")
    response = requests.get(f"{BASE_URL}/api/students/maintenance", headers=headers)
    if response.status_code != 200:
        print(f"❌ 查询失败: {response.text}")
        return
    
    requests_list = response.json()
    print(f"✅ 共有 {len(requests_list)} 个维修申请")
    
    # 找到一个待处理的申请
    pending_request = None
    for req in requests_list:
        if req["status"] in ["pending", "in_progress"]:
            pending_request = req
            break
    
    if not pending_request:
        # 创建一个新的维修申请
        print("\n3. 未找到待处理申请,创建新申请...")
        new_request_data = {
            "issue_type": "水电",
            "description": "水龙头漏水",
            "priority": "medium"
        }
        response = requests.post(
            f"{BASE_URL}/api/students/maintenance",
            json=new_request_data,
            headers=headers
        )
        if response.status_code != 201:
            print(f"❌ 创建失败: {response.text}")
            return
        pending_request = response.json()
        print(f"✅ 创建成功,申请ID: {pending_request['request_id']}")
    
    request_id = pending_request["request_id"]
    print(f"\n📋 当前申请信息:")
    print(f"   ID: {request_id}")
    print(f"   类型: {pending_request['issue_type']}")
    print(f"   描述: {pending_request['description']}")
    print(f"   优先级: {pending_request['priority']}")
    print(f"   状态: {pending_request['status']}")
    
    # 4. 修改维修申请
    print(f"\n4. 修改维修申请...")
    update_data = {
        "issue_type": "网络",
        "description": "宿舍网络经常断线,无法正常上网学习,已持续3天",
        "priority": "high"
    }
    response = requests.put(
        f"{BASE_URL}/api/students/maintenance/{request_id}",
        json=update_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 修改失败: {response.text}")
        return
    
    updated_request = response.json()
    print(f"✅ 修改成功!")
    print(f"\n📋 修改后信息:")
    print(f"   ID: {updated_request['request_id']}")
    print(f"   类型: {updated_request['issue_type']}")
    print(f"   描述: {updated_request['description']}")
    print(f"   优先级: {updated_request['priority']}")
    print(f"   状态: {updated_request['status']}")
    
    # 5. 测试部分更新
    print(f"\n5. 测试部分更新(仅修改优先级)...")
    partial_update = {
        "priority": "urgent"
    }
    response = requests.put(
        f"{BASE_URL}/api/students/maintenance/{request_id}",
        json=partial_update,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ 部分更新失败: {response.text}")
        return
    
    updated_request = response.json()
    print(f"✅ 部分更新成功!")
    print(f"   新优先级: {updated_request['priority']}")
    print(f"   描述未变: {updated_request['description']}")
    
    # 6. 测试修改已完成的申请(应该失败)
    print(f"\n6. 测试修改已完成申请(应该失败)...")
    completed_request = None
    for req in requests_list:
        if req["status"] == "completed":
            completed_request = req
            break
    
    if completed_request:
        response = requests.put(
            f"{BASE_URL}/api/students/maintenance/{completed_request['request_id']}",
            json={"priority": "high"},
            headers=headers
        )
        if response.status_code == 400:
            print(f"✅ 正确拦截了对已完成申请的修改")
            print(f"   错误信息: {response.json()['detail']}")
        else:
            print(f"⚠️  应该拦截但未拦截")
    else:
        print("⏭️  未找到已完成的申请,跳过此测试")
    
    print(f"\n{'='*70}")
    print("✅ 所有测试完成!")
    print("=" * 70)

if __name__ == "__main__":
    test_update_maintenance()
