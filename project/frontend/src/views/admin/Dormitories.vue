<template>
  <div class="dormitories-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><House /></el-icon>
          <span>Dormitory Management</span>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="Room No">
          <el-input v-model="searchForm.room_no" placeholder="Enter room no" clearable />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">Search</el-button>
          <el-button :icon="Refresh" @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- 宿舍列表 -->
      <el-table 
        :data="dormitories" 
        v-loading="loading"
        stripe
        border
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column prop="dorm_id" label="Dorm ID" width="100" />
        <el-table-column prop="building_no" label="Building" width="100" />
        <el-table-column prop="room_no" label="Room No" width="120" />
        <el-table-column prop="gender_type" label="Gender Type" width="100">
          <template #default="{ row }">
            <el-tag :type="row.gender_type === '男' ? 'primary' : 'danger'" size="small">
              {{ row.gender_type === '男' ? 'Male Dorm' : 'Female Dorm' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Bed Occupancy" width="200">
          <template #default="{ row }">
            <el-progress 
              :percentage="Math.round((row.occupied_beds / row.total_beds) * 100)" 
              :color="row.occupied_beds >= row.total_beds ? '#F56C6C' : '#67C23A'"
            >
              <span>{{ row.occupied_beds }}/{{ row.total_beds }}</span>
            </el-progress>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="150" show-overflow-tooltip />
        <el-table-column label="Actions" width="250" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              :icon="View"
              @click="viewResidents(row)"
            >
              View Residents
            </el-button>
            <el-button 
              type="info" 
              size="small" 
              :icon="View"
              @click="viewDormInfo(row)"
            >
              View Details
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
        @size-change="loadDormitories"
        @current-change="loadDormitories"
      />
    </el-card>

    <!-- 查看宿舍信息对话框 -->
      <el-dialog 
      v-model="dialogVisible" 
      title="Dorm Details" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="editForm" 
        :rules="rules" 
        ref="formRef" 
        label-width="100px"
      >
        <el-form-item label="Dorm ID">
          <el-input v-model="editForm.dorm_id" disabled />
        </el-form-item>
        <el-form-item label="Building" prop="building_no">
          <el-input v-model="editForm.building_no" disabled />
        </el-form-item>
        <el-form-item label="Room No" prop="room_no">
          <el-input v-model="editForm.room_no" disabled />
        </el-form-item>
        <el-form-item label="Gender Type" prop="gender_type">
          <el-radio-group v-model="editForm.gender_type" disabled>
            <el-radio label="男">Male Dorm</el-radio>
            <el-radio label="女">Female Dorm</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Total Beds" prop="total_beds">
          <el-input-number v-model="editForm.total_beds" :min="1" :max="8" disabled />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input 
            v-model="editForm.description" 
            type="textarea"
            :rows="3"
            placeholder="Description feature coming soon"
            disabled
          />
          <el-text type="info" size="small" style="margin-top: 5px">
            Note: Dorm description will be available in future versions
          </el-text>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <!-- 暂时隐藏保存按钮,因为没有可编辑字段 -->
        <!-- <el-button type="primary" @click="handleUpdate" :loading="submitting">
          保存修改
        </el-button> -->
      </template>
    </el-dialog>

    <!-- 查看住宿学生对话框 -->
      <el-dialog 
      v-model="residentsDialogVisible" 
      :title="`${currentDorm.room_no} Residents`" 
      width="600px"
    >
      <el-table :data="residents" stripe border>
        <el-table-column prop="student_id" label="Student ID" width="120" />
        <el-table-column prop="name" label="Name" width="100" />
        <el-table-column prop="gender" label="Gender" width="80" />
        <el-table-column prop="email" label="Email" min-width="180" />
        <el-table-column prop="college" label="College" width="120" />
      </el-table>
      <el-empty v-if="residents.length === 0" description="No students in this dorm" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { House, Search, Refresh, Edit, View } from '@element-plus/icons-vue'
import { getDormitories, updateDormitory, getDormitoryStudents } from '@/api/admin'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const residentsDialogVisible = ref(false)
const dormitories = ref([])
const residents = ref([])
const formRef = ref(null)

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const searchForm = reactive({
  room_no: '',
  gender_type: ''
})

const editForm = reactive({
  dorm_id: null,
  building_no: '',
  room_no: '',
  gender_type: '',
  total_beds: 4,
  description: ''
})

const currentDorm = ref({})

const rules = {
  description: [
    { max: 200, message: '描述长度不能超过200字', trigger: 'blur' }
  ]
}

onMounted(() => {
  loadDormitories()
})

const loadDormitories = async () => {
  try {
    loading.value = true
    
    // 将前端的分页参数转换为后端期望的skip和limit
    const skip = (currentPage.value - 1) * pageSize.value
    const limit = pageSize.value
    
    const params = { 
      skip: skip,
      limit: limit,
      ...searchForm 
    }
    
    Object.keys(params).forEach(key => {
      if (params[key] === '') delete params[key]
    })

    const data = await getDormitories(params)
    
    // 处理后端返回的数据格式
    if (data.items) {
      dormitories.value = data.items
      total.value = data.total
    } else if (Array.isArray(data)) {
      dormitories.value = data
      total.value = data.length
    } else if (data.dormitories) {
      dormitories.value = data.dormitories
      total.value = data.dormitories.length
    } else {
      dormitories.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('Failed to load dormitories:', error)
    ElMessage.error('Failed to load dormitories')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  loadDormitories()
}

const handleReset = () => {
  searchForm.room_no = ''
  searchForm.gender_type = ''
  currentPage.value = 1
  loadDormitories()
}

const openEditDialog = (dorm) => {
  editForm.dorm_id = dorm.dorm_id
  editForm.building_no = dorm.building_no
  editForm.room_no = dorm.room_no
  editForm.gender_type = dorm.gender_type
  editForm.total_beds = dorm.total_beds
  editForm.description = dorm.description || ''
  dialogVisible.value = true
}

// 重命名为更准确的函数名
const viewDormInfo = openEditDialog

const handleUpdate = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    await updateDormitory(editForm.dorm_id, {
      description: editForm.description
    })

    ElMessage.success('Dorm updated successfully')
    dialogVisible.value = false
    await loadDormitories()
  } catch (error) {
    if (error !== false) {
      console.error('Failed to update dormitory:', error)
      ElMessage.error('Failed to update dormitory')
    }
  } finally {
    submitting.value = false
  }
}

const viewResidents = async (dorm) => {
  try {
    currentDorm.value = dorm
    const data = await getDormitoryStudents(dorm.dorm_id)
    residents.value = Array.isArray(data) ? data : []
    residentsDialogVisible.value = true
  } catch (error) {
    console.error('Failed to load residents:', error)
    ElMessage.error('Failed to load residents')
  }
}
</script>

<style scoped>
.dormitories-page {
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
</style>
