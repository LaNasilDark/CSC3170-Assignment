<template>
  <div class="students-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><User /></el-icon>
          <span>Student Management</span>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="Search">
          <el-input 
            v-model="searchForm.search" 
            placeholder="Enter student ID or name" 
            clearable 
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="Gender">
          <el-select 
            v-model="searchForm.gender" 
            placeholder="Select gender" 
            clearable
            style="width: 120px"
          >
            <el-option label="Male" value="男" />
            <el-option label="Female" value="女" />
          </el-select>
        </el-form-item>
        <el-form-item label="College">
          <el-select 
            v-model="searchForm.college" 
            placeholder="Select college"
            clearable
            style="width: 180px"
          >
            <el-option label="Business School (SME)" value="SME" />
            <el-option label="Science & Engineering (SSE)" value="SSE" />
            <el-option label="Humanities & Social Sciences (HSS)" value="HSS" />
            <el-option label="Life & Health Sciences (SAI)" value="SAI" />
            <el-option label="Data Science (SDS)" value="SDS" />
            <el-option label="Medical School (MED)" value="MED" />
            <el-option label="Music (MUS)" value="MUS" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">Search</el-button>
          <el-button :icon="Refresh" @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- 学生列表 -->
      <el-table 
        :data="students" 
        v-loading="loading"
        stripe
        border
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column prop="student_id" label="Student ID" width="120" />
        <el-table-column prop="name" label="Name" width="100" />
        <el-table-column prop="gender" label="Gender" width="80">
          <template #default="{ row }">
            <el-tag :type="row.gender === '男' ? 'primary' : 'danger'" size="small">
              {{ row.gender }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="Email" min-width="180" />
        <el-table-column prop="college" label="College" width="150" />
        <el-table-column prop="dorm_id" label="Dorm ID" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.dorm_id" type="success" size="small">{{ row.dorm_id }}</el-tag>
            <el-tag v-else type="info" size="small">Unassigned</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              :icon="Edit"
              @click="openEditDialog(row)"
            >
              Edit
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              :icon="Delete"
              @click="handleDelete(row)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="loadStudents"
        @current-change="loadStudents"
      />
    </el-card>

    <!-- 编辑学生对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="Edit Student" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="editForm" 
        :rules="rules" 
        ref="formRef" 
        label-width="100px"
      >
        <el-form-item label="Student ID" prop="student_id">
          <el-input v-model="editForm.student_id" disabled />
        </el-form-item>
        <el-form-item label="Name" prop="name">
          <el-input v-model="editForm.name" placeholder="Enter name" />
        </el-form-item>
        <el-form-item label="Gender" prop="gender">
          <el-radio-group v-model="editForm.gender">
            <el-radio label="男">Male</el-radio>
            <el-radio label="女">Female</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Email" prop="email">
          <el-input v-model="editForm.email" placeholder="Enter email" />
        </el-form-item>
        <el-form-item label="College" prop="college">
          <el-select 
            v-model="editForm.college" 
            placeholder="Select college"
            style="width: 100%"
          >
            <el-option label="Business School (SME)" value="SME" />
            <el-option label="Science & Engineering (SSE)" value="SSE" />
            <el-option label="Humanities & Social Sciences (HSS)" value="HSS" />
            <el-option label="Life & Health Sciences (SAI)" value="SAI" />
            <el-option label="Data Science (SDS)" value="SDS" />
            <el-option label="Medical School (MED)" value="MED" />
            <el-option label="Music (MUS)" value="MUS" />
          </el-select>
        </el-form-item>
        <el-form-item label="Dorm ID" prop="dorm_id">
          <el-input-number 
            v-model="editForm.dorm_id" 
            :min="0"
            placeholder="Enter dorm ID, 0 means unassigned"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleUpdate" :loading="submitting">
          Save Changes
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { getStudents, updateStudent, deleteStudent } from '@/api/admin'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const students = ref([])
const formRef = ref(null)

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchForm = reactive({
  search: '',
  gender: '',
  college: ''
})

const editForm = reactive({
  student_id: '',
  name: '',
  gender: '',
  email: '',
  college: '',
  dorm_id: null
})

const rules = {
  name: [
    { required: true, message: 'Please enter name', trigger: 'blur' }
  ],
  gender: [
    { required: true, message: 'Please select gender', trigger: 'change' }
  ],
  email: [
    { required: true, message: 'Please enter email', trigger: 'blur' },
    { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
  ],
  college: [
    { required: true, message: 'Please enter college', trigger: 'blur' }
  ]
}

onMounted(() => {
  loadStudents()
})

const loadStudents = async () => {
  try {
    loading.value = true
    
    // 将前端的分页参数转换为后端期望的skip和limit
    const skip = (currentPage.value - 1) * pageSize.value
    const limit = pageSize.value
    
    // 构建搜索参数
    // 后端使用单一的search参数同时搜索学号和姓名
    const params = {
      skip: skip,
      limit: limit,
      search: searchForm.search,
      gender: searchForm.gender,
      college: searchForm.college
    }
    
    // 过滤空参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const data = await getStudents(params)
    
    // 处理后端返回的分页数据
    if (data.items) {
      students.value = data.items
      total.value = data.total
    } else if (data.students) {
      // 兼容其他可能的格式
      students.value = data.students
      total.value = data.total
    } else {
      // 如果后端直接返回数组，前端分页
      students.value = data
      total.value = data.length
    }
  } catch (error) {
    console.error('Failed to load students:', error)
    ElMessage.error('Failed to load students')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadStudents()
}

const handleReset = () => {
  searchForm.search = ''
  searchForm.gender = ''
  searchForm.college = ''
  currentPage.value = 1
  loadStudents()
}

const openEditDialog = (student) => {
  editForm.student_id = student.student_id
  editForm.name = student.name
  editForm.gender = student.gender
  editForm.email = student.email
  editForm.college = student.college
  editForm.dorm_id = student.dorm_id || null
  dialogVisible.value = true
}

const handleUpdate = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    await updateStudent(editForm.student_id, {
      name: editForm.name,
      gender: editForm.gender,
      email: editForm.email,
      college: editForm.college,
      dorm_id: editForm.dorm_id || null
    })

    ElMessage.success('Student updated successfully')
    dialogVisible.value = false
    await loadStudents()
  } catch (error) {
    if (error !== false) {
      console.error('Failed to update student:', error)
      ElMessage.error('Failed to update student')
    }
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (student) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete student ${student.name} (${student.student_id})? This action cannot be undone!`,
      'Warning',
      {
        confirmButtonText: 'Confirm',
        cancelButtonText: 'Cancel',
        type: 'warning',
      }
    )

    await deleteStudent(student.student_id)
    ElMessage.success('Student deleted successfully')
    await loadStudents()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete student:', error)
      ElMessage.error('Failed to delete student')
    }
  }
}
</script>

<style scoped>
.students-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.search-form {
  margin-top: 20px;
}

/* 确保表单项有足够的间距 */
.search-form .el-form-item {
  margin-right: 16px;
  margin-bottom: 12px;
}

/* 防止内容被挤压 */
.search-form .el-select,
.search-form .el-input {
  min-width: 0;
}
</style>
