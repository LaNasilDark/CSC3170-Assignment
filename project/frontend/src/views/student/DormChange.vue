<template>
  <div class="dorm-change-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Sort /></el-icon>
          <span>宿舍调换申请</span>
          <el-button 
            type="primary" 
            :icon="Plus" 
            @click="openDialog"
            style="margin-left: auto"
          >
            新建申请
          </el-button>
        </div>
      </template>

      <!-- 申请列表 -->
      <el-table 
        :data="requests" 
        v-loading="loading"
        stripe
      >
        <el-table-column prop="current_dorm_id" label="当前宿舍" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.current_dorm_info || row.current_dorm_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="target_dorm_id" label="目标宿舍" width="120">
          <template #default="{ row }">
            <el-tag type="success">{{ row.target_dorm_info || row.target_dorm_id }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="reason" label="申请理由" show-overflow-tooltip min-width="200" />

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="admin_comment" label="管理员备注" show-overflow-tooltip min-width="150">
          <template #default="{ row }">
            {{ row.admin_comment || '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="申请时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column prop="updated_at" label="处理时间" width="160">
          <template #default="{ row }">
            {{ row.status !== 'pending' ? formatDateTime(row.updated_at) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建申请对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="提交宿舍调换申请" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="form" 
        :rules="rules" 
        ref="formRef" 
        label-width="100px"
      >
        <el-form-item label="当前宿舍">
          <el-input v-model="currentDormInfo" disabled />
        </el-form-item>

        <el-form-item label="目标楼栋" prop="target_building">
          <el-select 
            v-model="form.target_building" 
            placeholder="请选择目标楼栋"
            style="width: 100%"
            :loading="!studentGender"
          >
            <el-option 
              v-for="building in availableBuildings" 
              :key="building" 
              :label="building" 
              :value="building"
            />
          </el-select>
          <div v-if="!studentGender" style="color: #e6a23c; font-size: 12px; margin-top: 4px">
            正在加载可选楼栋...
          </div>
          <div v-else-if="availableBuildings.length === 0" style="color: #f56c6c; font-size: 12px; margin-top: 4px">
            无可用楼栋(性别: {{ studentGender }})
          </div>
        </el-form-item>

        <el-form-item label="目标房间号" prop="target_room">
          <el-input 
            v-model="form.target_room" 
            placeholder="请输入房间号(如: 101)"
          />
          <div style="color: #909399; font-size: 12px; margin-top: 4px">
            提示: 请确保目标宿舍有空床位
          </div>
        </el-form-item>

        <el-form-item label="申请理由" prop="reason">
          <el-input 
            v-model="form.reason" 
            type="textarea" 
            :rows="4"
            placeholder="请详细说明调换宿舍的理由(5-500字)"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          提交申请
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
  console.log('computed - 当前性别:', gender, '类型:', typeof gender)
  
  if (gender === '男' || gender === 'male' || gender === 'M') {
    return ['MA', 'MB', 'MC', 'MD']
  } else if (gender === '女' || gender === 'female' || gender === 'F') {
    return ['FA', 'FB']
  }
  return []
})

const rules = {
  target_building: [
    { required: true, message: '请选择目标楼栋', trigger: 'change' }
  ],
  target_room: [
    { required: true, message: '请输入房间号', trigger: 'blur' },
    { pattern: /^\d+$/, message: '房间号必须是数字', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请输入申请理由', trigger: 'blur' },
    { min: 5, max: 500, message: '理由长度在5-500字之间', trigger: 'blur' }
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
    console.log('学生性别:', data.gender, '可用楼栋:', availableBuildings.value)
  } catch (error) {
    console.error('加载学生信息失败:', error)
  }
}

const loadRequests = async () => {
  try {
    loading.value = true
    const data = await getDormChangeRequests()
    requests.value = data
  } catch (error) {
    console.error('加载申请列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadCurrentDorm = async () => {
  try {
    const data = await getDormitory()
    if (data.building_no) {
      currentDormInfo.value = `${data.building_no} ${data.room_no}室 (ID: ${data.dorm_id})`
    } else {
      currentDormInfo.value = '未分配宿舍'
    }
  } catch (error) {
    console.error('加载宿舍信息失败:', error)
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
      ElMessage.error('未找到该宿舍，请检查楼栋和房间号是否正确')
      return
    }

    const targetDorm = dormResponse[0]
    
    // 检查性别是否匹配
    if (targetDorm.gender_type !== studentGender.value) {
      ElMessage.error(`该宿舍是${targetDorm.gender_type}生宿舍，与您的性别不匹配`)
      return
    }

    // 检查是否有空床位
    if (targetDorm.occupied_beds >= targetDorm.total_beds) {
      ElMessage.error('该宿舍已无空床位')
      return
    }

    // 提交申请
    await createDormChangeRequest({
      target_dorm_id: targetDorm.dorm_id,
      reason: form.reason
    })

    ElMessage.success('申请提交成功，请等待管理员审批')
    dialogVisible.value = false
    form.target_building = ''
    form.target_room = ''
    form.reason = ''
    await loadRequests()
  } catch (error) {
    if (error !== false) {
      console.error('提交申请失败:', error)
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
    'pending': '待审批',
    'approved': '已批准',
    'rejected': '已拒绝'
  }
  return textMap[status] || status
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
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
