<template>
  <div class="profile-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><User /></el-icon>
          <span>个人信息管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 基本信息 -->
        <el-tab-pane label="基本信息" name="profile">
          <el-form 
            :model="profileForm" 
            :rules="profileRules" 
            ref="profileFormRef" 
            label-width="100px"
            style="max-width: 600px; margin-top: 20px"
          >
            <el-form-item label="用户名">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="姓名" prop="name">
              <el-input v-model="profileForm.name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="电话" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入电话" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="submitting">
                保存修改
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 修改密码 -->
        <el-tab-pane label="修改密码" name="password">
          <el-form 
            :model="passwordForm" 
            :rules="passwordRules" 
            ref="passwordFormRef" 
            label-width="100px"
            style="max-width: 600px; margin-top: 20px"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input 
                v-model="passwordForm.old_password" 
                type="password" 
                placeholder="请输入当前密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input 
                v-model="passwordForm.new_password" 
                type="password" 
                placeholder="请输入新密码（至少6位）"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input 
                v-model="passwordForm.confirm_password" 
                type="password" 
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="submitting">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/api/auth'
import { updateAdminProfile, changeAdminPassword } from '@/api/admin'

const activeTab = ref('profile')
const submitting = ref(false)
const profileFormRef = ref(null)
const passwordFormRef = ref(null)

const profileForm = reactive({
  username: '',
  name: '',
  email: '',
  phone: ''
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const profileRules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

onMounted(() => {
  loadProfile()
})

const loadProfile = async () => {
  try {
    const data = await getCurrentUser()
    profileForm.username = data.username
    profileForm.name = data.name || ''
    profileForm.email = data.email || ''
    profileForm.phone = data.phone || ''
  } catch (error) {
    console.error('加载个人信息失败:', error)
  }
}

const handleUpdateProfile = async () => {
  try {
    await profileFormRef.value.validate()
    submitting.value = true

    await updateAdminProfile({
      name: profileForm.name,
      email: profileForm.email,
      phone: profileForm.phone
    })

    ElMessage.success('个人信息更新成功')
    window.location.reload()
  } catch (error) {
    if (error !== false) {
      console.error('更新个人信息失败:', error)
      ElMessage.error('更新个人信息失败')
    }
  } finally {
    submitting.value = false
  }
}

const handleChangePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    submitting.value = true

    await changeAdminPassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })

    ElMessage.success('密码修改成功，请重新登录')
    
    // 清除认证信息并跳转到登录页
    setTimeout(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('userType')
      window.location.href = '/login'
    }, 1500)
  } catch (error) {
    if (error !== false) {
      console.error('修改密码失败:', error)
      ElMessage.error('修改密码失败，请检查当前密码是否正确')
    }
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.profile-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}
</style>
