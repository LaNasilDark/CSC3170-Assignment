<template>
  <div class="dorm-change-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon>
            <Sort />
          </el-icon>
          <span>Dorm Change Requests</span>
          <el-button type="primary" :icon="Plus" @click="openDialog" style="margin-left: auto">
            New Request
          </el-button>
        </div>
      </template>

      <!-- Request list -->
      <el-table :data="requests" v-loading="loading" stripe>
        <el-table-column prop="current_dorm_id" label="Current Dorm" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.current_dorm_info || row.current_dorm_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="target_dorm_id" label="Target Dorm" width="120">
          <template #default="{ row }">
            <el-tag type="success">{{ row.target_dorm_info || row.target_dorm_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="reason" label="Reason" show-overflow-tooltip min-width="200" />

        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="admin_comment" label="Admin Comment" show-overflow-tooltip min-width="150">
          <template #default="{ row }">
            {{ row.admin_comment || '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="Request Time" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column prop="updated_at" label="Processed Time" width="160">
          <template #default="{ row }">
            {{ row.status !== 'pending' ? formatDateTime(row.updated_at) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建申请对话框 -->
    <el-dialog v-model="dialogVisible" title="Submit Dorm Change Request" width="500px" :close-on-click-modal="false">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="Current Dorm">
          <el-input v-model="currentDormInfo" disabled />
        </el-form-item>

        <el-form-item label="Target Building" prop="target_building">
          <el-select v-model="form.target_building" placeholder="Please select target building" style="width: 100%"
            :loading="!studentGender">
            <el-option v-for="building in availableBuildings" :key="building" :label="building" :value="building" />
          </el-select>
          <div v-if="!studentGender" style="color: #e6a23c; font-size: 12px; margin-top: 4px">
            Loading available buildings...
          </div>
          <div v-else-if="availableBuildings.length === 0" style="color: #f56c6c; font-size: 12px; margin-top: 4px">
            No available buildings (Gender: {{ studentGender }})
          </div>
        </el-form-item>

        <el-form-item label="Target Room" prop="target_room">
          <el-input v-model="form.target_room" placeholder="Enter room number (e.g., 101)" />
          <div style="color: #909399; font-size: 12px; margin-top: 4px">
            Tip: Ensure the target dorm has available beds
          </div>
        </el-form-item>

        <el-form-item label="Reason" prop="reason">
          <el-input v-model="form.reason" type="textarea" :rows="4"
            placeholder="Please explain the reason for the change (5-500 chars)" maxlength="500" show-word-limit />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          Submit Request
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Sort, Plus } from '@element-plus/icons-vue'
import { getDormChangeRequests, createDormChangeRequest, getDormitory } from '@/api/student'
import { getCurrentUser } from '@/api/auth'
import request from '@/utils/request'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const requests = ref([])
const formRef = ref(null)
const currentDormInfo = ref('')
const studentGender = ref('')

const form = reactive({
  target_building: '',
  target_room: '',
  reason: ''
})

// 根据性别显示可选楼栋
const availableBuildings = computed(() => {
  const gender = studentGender.value
  console.log('computed - gender:', gender, 'type:', typeof gender)

  if (gender === '男' || gender === 'male' || gender === 'M') {
    return ['MA', 'MB', 'MC', 'MD']
  } else if (gender === '女' || gender === 'female' || gender === 'F') {
    return ['FA', 'FB']
  }
  return []
})

const rules = {
  target_building: [
    { required: true, message: 'Please select a target building', trigger: 'change' }
  ],
  target_room: [
    { required: true, message: 'Please enter room number', trigger: 'blur' },
    { pattern: /^\d+$/, message: 'Room number must be numeric', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: 'Please enter a reason', trigger: 'blur' },
    { min: 5, max: 500, message: 'Reason length must be between 5 and 500 characters', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await loadStudentInfo()
  await loadRequests()
  await loadCurrentDorm()
})

const loadStudentInfo = async () => {
  try {
    const data = await getCurrentUser()
    studentGender.value = data.gender
    console.log('Student gender:', data.gender, 'available buildings:', availableBuildings.value)
  } catch (error) {
    console.error('Failed to load student info:', error)
  }
}

const loadRequests = async () => {
  try {
    loading.value = true
    const data = await getDormChangeRequests()
    requests.value = data
  } catch (error) {
    console.error('Failed to load requests:', error)
  } finally {
    loading.value = false
  }
}

const loadCurrentDorm = async () => {
  try {
    const data = await getDormitory()
    if (data.building_no) {
      currentDormInfo.value = `${data.building_no} ${data.room_no} (ID: ${data.dorm_id})`
    } else {
      currentDormInfo.value = 'Unassigned'
    }
  } catch (error) {
    console.error('Failed to load dormitory info:', error)
  }
}

const openDialog = async () => {
  // 确保性别信息已加载
  if (!studentGender.value) {
    await loadStudentInfo()
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    // 拼接完整的房间号（楼栋+房间号，如 MB505）
    const fullRoomNo = form.target_building + form.target_room

    // 根据楼栋和房间号查询宿舍ID（使用学生端API）
    const dormResponse = await request({
      url: '/students/dormitories',
      method: 'get',
      params: {
        building_no: form.target_building,
        room_no: fullRoomNo
      }
    })

    if (!dormResponse || dormResponse.length === 0) {
      ElMessage.error('Dorm not found, please check building and room number')
      return
    }

    const targetDorm = dormResponse[0]

    // 检查性别是否匹配
    if (targetDorm.gender_type !== studentGender.value) {
      ElMessage.error(`This dorm is for ${targetDorm.gender_type} students and does not match your gender`)
      return
    }

    // 检查是否有空床位
    if (targetDorm.occupied_beds >= targetDorm.total_beds) {
      ElMessage.error('No available beds in this dorm')
      return
    }

    // 提交申请
    await createDormChangeRequest({
      target_dorm_id: targetDorm.dorm_id,
      reason: form.reason
    })

    ElMessage.success('Request submitted successfully. Please wait for admin approval')
    dialogVisible.value = false
    form.target_building = ''
    form.target_room = ''
    form.reason = ''
    await loadRequests()
  } catch (error) {
    if (error !== false) {
      console.error('Failed to submit request:', error)
      if (error.response?.data?.detail) {
        ElMessage.error(error.response.data.detail)
      }
    }
  } finally {
    submitting.value = false
  }
}

const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'approved': 'success',
    'rejected': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'pending': 'Pending',
    'approved': 'Approved',
    'rejected': 'Rejected'
  }
  return textMap[status] || status
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('en-US')
}
</script>

<style scoped>
.dorm-change-page {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
</style>
