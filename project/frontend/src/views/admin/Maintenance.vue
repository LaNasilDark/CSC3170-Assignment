<template>
  <div class="maintenance-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Tools /></el-icon>
          <span>维修申请管理</span>
        </div>
      </template>

      <!-- 筛选 -->
      <el-radio-group v-model="statusFilter" @change="loadRequests" style="margin-bottom: 20px">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="pending">待处理</el-radio-button>
        <el-radio-button label="in_progress">处理中</el-radio-button>
        <el-radio-button label="completed">已完成</el-radio-button>
      </el-radio-group>

      <!-- 申请列表 -->
      <el-table 
        :data="filteredRequests" 
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="request_id" label="ID" width="60" />
        <el-table-column label="学生" width="150">
          <template #default="{ row }">
            {{ row.student_name }} ({{ row.student_id }})
          </template>
        </el-table-column>
        <el-table-column prop="issue_type" label="问题类型" width="100" />
        <el-table-column prop="description" label="问题描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              :icon="Edit"
              @click="openDialog(row)"
            >
              处理
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 处理对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      title="处理维修申请" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="申请ID">
          <el-input v-model="form.request_id" disabled />
        </el-form-item>
        <el-form-item label="问题类型">
          <el-input v-model="form.issue_type" disabled />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input v-model="form.description" type="textarea" :rows="3" disabled />
        </el-form-item>
        <el-form-item label="当前状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待处理" value="pending" />
            <el-option label="处理中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员备注">
          <el-input 
            v-model="form.admin_comment" 
            type="textarea"
            :rows="4"
            placeholder="请输入处理备注"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Tools, Edit } from '@element-plus/icons-vue'
import { getMaintenanceRequests, updateMaintenanceStatus } from '@/api/admin'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const requests = ref([])
const statusFilter = ref('all')

const form = ref({
  request_id: null,
  issue_type: '',
  description: '',
  status: '',
  admin_comment: ''
})

const filteredRequests = computed(() => {
  if (statusFilter.value === 'all') return requests.value
  return requests.value.filter(req => req.status === statusFilter.value)
})

onMounted(() => {
  loadRequests()
})

const loadRequests = async () => {
  try {
    loading.value = true
    const data = await getMaintenanceRequests()
    requests.value = data
  } catch (error) {
    console.error('加载维修申请失败:', error)
    ElMessage.error('加载维修申请失败')
  } finally {
    loading.value = false
  }
}

const openDialog = (request) => {
  form.value = {
    request_id: request.request_id,
    issue_type: request.issue_type,
    description: request.description,
    status: request.status,
    admin_comment: request.admin_comment || ''
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    submitting.value = true
    await updateMaintenanceStatus(form.value.request_id, {
      status: form.value.status,
      admin_comment: form.value.admin_comment
    })
    ElMessage.success('更新成功')
    dialogVisible.value = false
    await loadRequests()
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败')
  } finally {
    submitting.value = false
  }
}

const getPriorityType = (priority) => {
  const types = { high: 'danger', medium: 'warning', low: 'info' }
  return types[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = { high: '高', medium: '中', low: '低' }
  return texts[priority] || priority
}

const getStatusType = (status) => {
  const types = { pending: 'warning', in_progress: 'primary', completed: 'success' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { pending: '待处理', in_progress: '处理中', completed: '已完成' }
  return texts[status] || status
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('zh-CN')
}
</script>

<style scoped>
.maintenance-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}
</style>
