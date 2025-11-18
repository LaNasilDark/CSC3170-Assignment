<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="header-left">
        <el-icon style="font-size: 24px; margin-right: 10px"><HomeFilled /></el-icon>
        <span class="title">宿舍管理系统 - 学生端</span>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-dropdown">
            <el-icon><User /></el-icon>
            {{ userName }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人信息</el-dropdown-item>
              <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    
    <el-container>
      <el-aside width="200px" class="sidebar">
        <el-menu 
          :default-active="$route.path" 
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
        >
          <el-menu-item index="/student/dashboard">
            <el-icon><DataLine /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/student/profile">
            <el-icon><User /></el-icon>
            <span>个人信息</span>
          </el-menu-item>
          <el-menu-item index="/student/dormitory">
            <el-icon><House /></el-icon>
            <span>我的宿舍</span>
          </el-menu-item>
          <el-menu-item index="/student/bills">
            <el-icon><Tickets /></el-icon>
            <span>账单查询</span>
          </el-menu-item>
          <el-menu-item index="/student/dorm-change">
            <el-icon><Sort /></el-icon>
            <span>宿舍调换</span>
          </el-menu-item>
          <el-menu-item index="/student/maintenance">
            <el-icon><Tools /></el-icon>
            <span>维修申请</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { HomeFilled, User, ArrowDown, DataLine, House, Tickets, Sort, Tools } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/api/auth'
import { clearAuth } from '@/utils/auth'

const router = useRouter()
const userName = ref('学生')

onMounted(async () => {
  try {
    const data = await getCurrentUser()
    userName.value = data.name || data.student_id
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
})

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/student/profile')
  } else if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      clearAuth()
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      // 用户取消
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 4px;
}

.user-dropdown:hover {
  background-color: #f5f7fa;
}

.sidebar {
  background-color: #304156;
  overflow-x: hidden;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
