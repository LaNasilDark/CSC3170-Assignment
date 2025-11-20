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
        <el-tab-pane label="基本信息" name="info">
          <el-form 
            :model="profileForm" 
            :rules="profileRules" 
            ref="profileFormRef" 
            label-width="120px"
            v-loading="loading"
          >
            <el-form-item label="学号">
              <el-input v-model="profileForm.student_id" disabled />
            </el-form-item>

            <el-form-item label="姓名" prop="name">
              <el-input v-model="profileForm.name" placeholder="请输入姓名" />
            </el-form-item>

            <el-form-item label="性别">
              <el-input v-model="profileForm.gender" disabled />
            </el-form-item>

            <el-form-item label="国籍">
              <el-input v-model="profileForm.nationality" disabled />
            </el-form-item>

            <el-form-item label="学院">
              <el-input v-model="profileForm.college" disabled />
            </el-form-item>

            <el-form-item label="入学年份">
              <el-input v-model="profileForm.enrollment_year" disabled />
            </el-form-item>

            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>

            <el-form-item label="宿舍">
              <el-input v-model="dormInfo" disabled />
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile" :loading="submitting">
                保存修改
              </el-button>
              <el-button @click="loadProfile">取消</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 修改密码 -->
        <el-tab-pane label="修改密码" name="password">
          <el-form 
            :model="passwordForm" 
            :rules="passwordRules" 
            ref="passwordFormRef" 
            label-width="120px"
          >
            <el-form-item label="旧密码" prop="old_password">
              <el-input 
                v-model="passwordForm.old_password" 
                type="password" 
                placeholder="请输入旧密码"
                show-password
              />
            </el-form-item>

            <el-form-item label="新密码" prop="new_password">
              <el-input 
                v-model="passwordForm.new_password" 
                type="password" 
                placeholder="请输入新密码(至少6位)"
                show-password
              />
            </el-form-item>

            <el-form-item label="确认新密码" prop="confirm_password">
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
              <el-button @click="resetPasswordForm">重置</el-button>
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

const dormInfo = ref('未分配')

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
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, message: '姓名至少2个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
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
    console.error('加载个人信息失败:', error)
  } finally {
    loading.value = false
  }
}

const loadDormitory = async () => {
  try {
    const data = await getDormitory()
    if (data.building_no) {
      dormInfo.value = `${data.building_no} ${data.room_no}室`
    }
  } catch (error) {
    console.error('加载宿舍信息失败:', error)
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

    ElMessage.success('个人信息更新成功')
    await loadProfile()
    
    // 刷新页面以更新右上角的用户名显示
    window.location.reload()
  } catch (error) {
    if (error !== false) { // 不是表单验证失败
      console.error('更新个人信息失败:', error)
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

    ElMessage.success('密码修改成功')
    resetPasswordForm()
  } catch (error) {
    if (error !== false) {
      console.error('修改密码失败:', error)
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
