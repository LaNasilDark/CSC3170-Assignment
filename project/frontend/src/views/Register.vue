<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>🎓 Student Registration</h2>
          <!-- <p>Student Registration</p> -->
        </div>
      </template>
      
      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="150px">
        <el-form-item label="Student ID" prop="student_id">
          <el-input 
            v-model="registerForm.student_id" 
            placeholder="Please enter your 9-digit Student ID"
            maxlength="9"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="Please enter a password with at least 6 characters"
            show-password
          />
        </el-form-item>
        
        <el-form-item label=" Password Confirm" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="Please confirm your password"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="Name" prop="name">
          <el-input v-model="registerForm.name" placeholder="Please enter your name" clearable />
        </el-form-item>
        
        <el-form-item label="Gender" prop="gender">
          <el-radio-group v-model="registerForm.gender">
            <el-radio label="男">Male</el-radio>
            <el-radio label="女">Female</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="Nationality" prop="nationality">
          <el-input v-model="registerForm.nationality" placeholder="Please enter your nationality" clearable />
        </el-form-item>
        
        <el-form-item label="School" prop="college">
          <el-select v-model="registerForm.college" placeholder="Please select your school" style="width: 100%">
            <el-option label="SSE" value="SSE" />
            <el-option label="SME" value="SME" />
            <el-option label="MED" value="MED" />
            <el-option label="HSS" value="HSS" />
            <el-option label="SAI" value="SAI" />
            <el-option label="SDS" value="SDS" />
            <el-option label="MUS" value="MUS" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Enrollment Year" prop="enrollment_year">
          <el-select v-model="registerForm.enrollment_year" placeholder="Please select your year of enrollment" style="width: 100%">
            <el-option :label="year" :value="year" v-for="year in years" :key="year" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Email" prop="email">
          <el-input v-model="registerForm.email" placeholder="Please enter your email address" clearable />
        </el-form-item>
        
        <el-alert 
          title="Your dormitory will be automatically assigned upon successful registration" 
          type="info" 
          :closable="false"
          style="margin-bottom: 20px"
        />
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleRegister"
            style="width: 100%"
          >
            {{ loading ? 'Registering...' : 'Register' }}
          </el-button>
        </el-form-item>
        
        <div class="login-link">
          Already have an account?
          <router-link to="/login">Login now</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register } from '@/api/auth'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)

const registerForm = reactive({
  student_id: '',
  password: '',
  confirmPassword: '',
  name: '',
  gender: '',
  nationality: '',
  college: '',
  enrollment_year: null,
  email: ''
})

// Generate year options (last 10 years)
const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 10 }, (_, i) => currentYear - i)
})

// Custom validation rules
const validateStudentId = (rule, value, callback) => {
  if (!/^\d{9}$/.test(value)) {
    callback(new Error('Student ID must be 9 digits'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

const rules = {
  student_id: [
    { required: true, message: 'Please enter Student ID', trigger: 'blur' },
    { validator: validateStudentId, trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: 'Please confirm your password', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  name: [
    { required: true, message: 'Please enter your name', trigger: 'blur' },
    { min: 2, message: 'Name must be at least 2 characters', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: 'Please select gender', trigger: 'change' }
  ],
  nationality: [
    { required: true, message: 'Please enter nationality', trigger: 'blur' }
  ],
  college: [
    { required: true, message: 'Please select your school', trigger: 'change' }
  ],
  enrollment_year: [
    { required: true, message: 'Please select enrollment year', trigger: 'change' }
  ],
  email: [
    { required: true, message: 'Please enter email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    // remove confirmPassword field
    const { confirmPassword, ...submitData } = registerForm
    
    const data = await register(submitData)
    
    ElMessage.success('Registration successful! Your dormitory has been automatically assigned. Please log in to view.')
    
    // 跳转到登录页
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    console.error('Registration failed:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 0;
}

.register-card {
  width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-link {
  text-align: center;
  color: #909399;
  font-size: 14px;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
