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
            @click="dialogVisible = true"
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

        <el-form-item label="目标宿舍ID" prop="target_dorm_id">
          <el-input 
            v-model.number="form.target_dorm_id" 
            placeholder="请输入目标宿舍ID"
            type="number"
          />
          <div style="color: #909399; font-size: 12px; margin-top: 4px">
            提示: 请确保目标宿舍性别类型匹配且有空床位
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Sort, Plus } from '@element-plus/icons-vue'
import { getDormChangeRequests, createDormChangeRequest, getDormitory } from '@/api/student'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const requests = ref([])
const formRef = ref(null)
const currentDormInfo = ref('')

const form = reactive({
  target_dorm_id: null,
  reason: ''
})

const rules = {
  target_dorm_id: [
    { required: true, message: '请输入目标宿舍ID', trigger: 'blur' },
    { type: 'number', message: '宿舍ID必须是数字', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请输入申请理由', trigger: 'blur' },
    { min: 5, max: 500, message: '理由长度在5-500字之间', trigger: 'blur' }
  ]
}

onMounted(async () => {
  await loadRequests()
  await loadCurrentDorm()
})

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

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    await createDormChangeRequest(form)

    ElMessage.success('申请提交成功，请等待管理员审批')
    dialogVisible.value = false
    form.target_dorm_id = null
    form.reason = ''
    await loadRequests()
  } catch (error) {
    if (error !== false) {
      console.error('提交申请失败:', error)
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
