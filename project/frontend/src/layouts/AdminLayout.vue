<template>
  <el-container class="layout-container">
    <el-header class="header">
        <div class="header-left">
        <el-icon style="font-size: 24px; margin-right: 10px"><Setting /></el-icon>
        <span class="title">Dormitory Management System - Admin Panel</span>
      </div>
      <div class="header-right">
        <el-dropdown @command="handleCommand">
          <span class="user-dropdown">
            <el-icon><UserFilled /></el-icon>
            {{ userName }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">Profile</el-dropdown-item>
              <el-dropdown-item command="logout" divided>Logout</el-dropdown-item>
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
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>Overview</span>
          </el-menu-item>
          <el-menu-item index="/admin/students">
            <el-icon><User /></el-icon>
            <span>Students</span>
          </el-menu-item>
          <el-menu-item index="/admin/dormitories">
            <el-icon><House /></el-icon>
            <span>Dormitories</span>
          </el-menu-item>
          <el-menu-item index="/admin/dorm-requests">
            <el-icon><Sort /></el-icon>
            <span>Dorm Change Approvals</span>
          </el-menu-item>
          <el-menu-item index="/admin/maintenance">
            <el-icon><Tools /></el-icon>
            <span>Maintenance</span>
          </el-menu-item>
          <el-menu-item index="/admin/bills">
            <el-icon><Tickets /></el-icon>
            <span>Bills</span>
          </el-menu-item>
          <el-menu-item index="/admin/profile">
            <el-icon><Setting /></el-icon>
            <span>Profile</span>
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
import { Setting, UserFilled, ArrowDown, DataAnalysis, User, House, Sort, Tools, Tickets } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/api/auth'
import { clearAuth } from '@/utils/auth'

const router = useRouter()
const userName = ref('Administrator')

onMounted(async () => {
  try {
    const data = await getCurrentUser()
    userName.value = data.name || data.username
  } catch (error) {
    console.error('Failed to get user info:', error)
  }
})

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/admin/profile')
  } else if (command === 'logout') {
      try {
      await ElMessageBox.confirm('Are you sure you want to log out?', 'Confirm', {
        confirmButtonText: 'OK',
        cancelButtonText: 'Cancel',
        type: 'warning'
      })
      clearAuth()
      ElMessage.success('Logged out')
      router.push('/login')
    } catch (error) {
      // user cancelled
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
