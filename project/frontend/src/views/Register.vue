<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <h2>🎓 学生注册</h2>
          <p>Student Registration</p>
        </div>
      </template>
      
      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="100px">
        <el-form-item label="学号" prop="student_id">
          <el-input 
            v-model="registerForm.student_id" 
            placeholder="请输入9位学号"
            maxlength="9"
            clearable
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="至少6位密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="再次输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="name">
          <el-input v-model="registerForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="registerForm.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="国籍" prop="nationality">
          <el-input v-model="registerForm.nationality" placeholder="请输入国籍" clearable />
        </el-form-item>
        
        <el-form-item label="学院" prop="college">
          <el-select v-model="registerForm.college" placeholder="请选择学院" style="width: 100%">
            <el-option label="理工学院 (SSE)" value="SSE" />
            <el-option label="管理学院 (SME)" value="SME" />
            <el-option label="医学院 (MED)" value="MED" />
            <el-option label="人文社科学院 (HSS)" value="HSS" />
            <el-option label="人工智能学院 (SAI)" value="SAI" />
            <el-option label="数据科学学院 (SDS)" value="SDS" />
            <el-option label="音乐学院 (MUS)" value="MUS" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="入学年份" prop="enrollment_year">
          <el-select v-model="registerForm.enrollment_year" placeholder="请选择入学年份" style="width: 100%">
            <el-option :label="year" :value="year" v-for="year in years" :key="year" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" placeholder="example@cuhk.edu.cn" clearable />
        </el-form-item>
        
        <el-alert 
          title="注册成功后将自动为您分配宿舍" 
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
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
        </el-form-item>
        
        <div class="login-link">
          已有账号？
          <router-link to="/login">立即登录</router-link>
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

// 生成年份选项（最近10年）
const years = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 10 }, (_, i) => currentYear - i)
})

// 自定义验证规则
const validateStudentId = (rule, value, callback) => {
  if (!/^\d{9}$/.test(value)) {
    callback(new Error('学号必须是9位数字'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateEmail = (rule, value, callback) => {
  if (!value.endsWith('@cuhk.edu.cn')) {
    callback(new Error('必须使用学校邮箱(@cuhk.edu.cn)'))
  } else {
    callback()
  }
}

const rules = {
  student_id: [
    { required: true, message: '请输入学号', trigger: 'blur' },
    { validator: validateStudentId, trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, message: '姓名至少2个字符', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: '请选择性别', trigger: 'change' }
  ],
  nationality: [
    { required: true, message: '请输入国籍', trigger: 'blur' }
  ],
  college: [
    { required: true, message: '请选择学院', trigger: 'change' }
  ],
  enrollment_year: [
    { required: true, message: '请选择入学年份', trigger: 'change' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
    { validator: validateEmail, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    // 移除确认密码字段
    const { confirmPassword, ...submitData } = registerForm
    
    const data = await register(submitData)
    
    ElMessage.success('注册成功！已自动为您分配宿舍，请登录查看')
    
    // 跳转到登录页
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    console.error('注册失败:', error)
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
