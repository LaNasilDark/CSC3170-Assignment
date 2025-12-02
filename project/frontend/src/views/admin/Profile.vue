<template>
  <div class="profile-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><User /></el-icon>
          <span>Profile Management</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- Basic Info -->
        <el-tab-pane label="Basic Info" name="profile">
          <el-form 
            :model="profileForm" 
            :rules="profileRules" 
            ref="profileFormRef" 
            label-width="100px"
            style="max-width: 600px; margin-top: 20px"
          >
            <el-form-item label="Username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="Name" prop="name">
              <el-input v-model="profileForm.name" placeholder="Enter name" />
            </el-form-item>
            <el-form-item label="Email" prop="email">
              <el-input v-model="profileForm.email" placeholder="Enter email" />
            </el-form-item>
            <el-form-item label="Phone" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="Enter phone" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="submitting">
                Save Changes
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Change Password -->
        <el-tab-pane label="Change Password" name="password">
          <el-form 
            :model="passwordForm" 
            :rules="passwordRules" 
            ref="passwordFormRef" 
            label-width="100px"
            style="max-width: 600px; margin-top: 20px"
          >
            <el-form-item label="Current Password" prop="old_password">
              <el-input 
                v-model="passwordForm.old_password" 
                type="password" 
                placeholder="Enter current password"
                show-password
              />
            </el-form-item>
            <el-form-item label="New Password" prop="new_password">
              <el-input 
                v-model="passwordForm.new_password" 
                type="password" 
                placeholder="Enter new password (at least 6 characters)"
                show-password
              />
            </el-form-item>
            <el-form-item label="Confirm Password" prop="confirm_password">
              <el-input 
                v-model="passwordForm.confirm_password" 
                type="password" 
                placeholder="Confirm new password"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="submitting">
                Change Password
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
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

const profileRules = {
  name: [
    { required: true, message: 'Please enter name', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: 'Please enter current password', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: 'Please enter new password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: 'Please confirm the new password', trigger: 'blur' },
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
    console.error('Failed to load profile:', error)
  }
}

const handleUpdateProfile = async () => {
  try {
    await profileFormRef.value.validate()
    submitting.value = true

    // 只发送非空字段
    const updateData = {}
    if (profileForm.name) updateData.name = profileForm.name
    if (profileForm.email) updateData.email = profileForm.email
    if (profileForm.phone) updateData.phone = profileForm.phone

    await updateAdminProfile(updateData)

    ElMessage.success('Profile updated successfully')
    window.location.reload()
  } catch (error) {
    if (error !== false) {
      console.error('Failed to update profile:', error)
      ElMessage.error('Failed to update profile')
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

    ElMessage.success('Password changed successfully, please log in again')
    
    // clear auth and redirect to login
    setTimeout(() => {
      localStorage.removeItem('token')
      localStorage.removeItem('userType')
      window.location.href = '/login'
    }, 1500)
  } catch (error) {
    if (error !== false) {
      console.error('Failed to change password:', error)
      ElMessage.error('Failed to change password, please check current password')
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
