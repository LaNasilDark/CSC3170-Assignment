<template>
  <div class="profile-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon>
            <User />
          </el-icon>
          <span>Profile Management</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <!-- Basic Info -->
        <el-tab-pane label="Basic Info" name="info">
          <el-form :model="profileForm" :rules="profileRules" ref="profileFormRef" label-width="120px"
            v-loading="loading">
            <el-form-item label="Student ID">
              <el-input v-model="profileForm.student_id" disabled />
            </el-form-item>

            <el-form-item label="Name" prop="name">
              <el-input v-model="profileForm.name" placeholder="Please enter name" />
            </el-form-item>

            <el-form-item label="Gender">
              <el-input v-model="profileForm.gender" disabled />
            </el-form-item>

            <el-form-item label="Nationality">
              <el-input v-model="profileForm.nationality" disabled />
            </el-form-item>

            <el-form-item label="College">
              <el-input v-model="profileForm.college" disabled />
            </el-form-item>

            <el-form-item label="Enrollment Year">
              <el-input v-model="profileForm.enrollment_year" disabled />
            </el-form-item>

            <el-form-item label="Email" prop="email">
              <el-input v-model="profileForm.email" placeholder="Please enter email" />
            </el-form-item>

            <el-form-item label="Dorm">
              <el-input v-model="dormInfo" disabled />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="submitting">
                Save Changes
              </el-button>
              <el-button @click="loadProfile">Cancel</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Change Password -->
        <el-tab-pane label="Change Password" name="password">
          <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px">
            <el-form-item label="Current Password" prop="old_password">
              <el-input v-model="passwordForm.old_password" type="password" placeholder="Enter current password"
                show-password />
            </el-form-item>

            <el-form-item label="New Password" prop="new_password">
              <el-input v-model="passwordForm.new_password" type="password"
                placeholder="Enter new password (min 6 chars)" show-password />
            </el-form-item>

            <el-form-item label="Confirm New Password" prop="confirm_password">
              <el-input v-model="passwordForm.confirm_password" type="password"
                placeholder="Please enter new password again" show-password />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleChangePassword" :loading="submitting">
                Change Password
              </el-button>
              <el-button @click="resetPasswordForm">Reset</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/api/auth'
import { getProfile, updateProfile, changePassword, getDormitory } from '@/api/student'

const activeTab = ref('info')
const loading = ref(false)
const submitting = ref(false)
const profileFormRef = ref(null)
const passwordFormRef = ref(null)

const profileForm = reactive({
  student_id: '',
  name: '',
  gender: '',
  nationality: '',
  college: '',
  enrollment_year: null,
  email: '',
  dorm_id: null
})

const dormInfo = ref('Unassigned')

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
    { required: true, message: 'Please enter name', trigger: 'blur' },
    { min: 2, message: 'Name must be at least 2 characters', trigger: 'blur' }
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
    { required: true, message: 'Please enter new password again', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

onMounted(async () => {
  await loadProfile()
  await loadDormitory()
})

const loadProfile = async () => {
  try {
    loading.value = true
    const data = await getProfile()
    Object.assign(profileForm, data)
  } catch (error) {
    console.error('Failed to load profile:', error)
  } finally {
    loading.value = false
  }
}

const loadDormitory = async () => {
  try {
    const data = await getDormitory()
    if (data.building_no) {
      dormInfo.value = `${data.building_no} ${data.room_no}`
    }
  } catch (error) {
    console.error('Failed to load dormitory info:', error)
  }
}

const handleUpdateProfile = async () => {
  try {
    await profileFormRef.value.validate()
    submitting.value = true

    await updateProfile({
      name: profileForm.name,
      email: profileForm.email
    })

    ElMessage.success('Profile updated successfully')
    await loadProfile()

    // 刷新页面以更新右上角的用户名显示
    window.location.reload()
  } catch (error) {
    if (error !== false) { // not a form validation failure
      console.error('Failed to update profile:', error)
    }
  } finally {
    submitting.value = false
  }
}

const handleChangePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    submitting.value = true

    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password
    })

    ElMessage.success('Password changed successfully')
    resetPasswordForm()
  } catch (error) {
    if (error !== false) {
      console.error('Failed to change password:', error)
    }
  } finally {
    submitting.value = false
  }
}

const resetPasswordForm = () => {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  passwordFormRef.value?.clearValidate()
}
</script>

<style scoped>
.profile-page {
  max-width: 800px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
</style>
