<template>
  <div class="maintenance-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon>
            <Tools />
          </el-icon>
          <span>Maintenance Requests</span>
          <el-button type="primary" :icon="Plus" @click="openDialog()" style="margin-left: auto">
            New Maintenance Request
          </el-button>
        </div>
      </template>

      <!-- Request list -->
      <el-timeline>
        <el-timeline-item v-for="request in requests" :key="request.request_id"
          :timestamp="formatDateTime(request.created_at)" placement="top" :type="getTimelineType(request.status)"
          :icon="getStatusIcon(request.status)">
          <el-card>
            <div class="request-header">
              <el-tag :type="getPriorityType(request.priority)" size="large">
                {{ getPriorityText(request.priority) }} Priority
              </el-tag>
              <el-tag :type="getStatusType(request.status)" size="large">
                {{ getStatusText(request.status) }}
              </el-tag>
              <el-button v-if="request.status === 'pending'" type="primary" size="small" :icon="Edit"
                @click="openDialog(request)" style="margin-left: auto">
                Edit
              </el-button>
            </div>

            <el-descriptions :column="2" border style="margin-top: 15px">
              <el-descriptions-item label="Issue Type">
                {{ request.issue_type }}
              </el-descriptions-item>
              <el-descriptions-item label="Submitted At">
                {{ formatDateTime(request.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="Description" :span="2">
                {{ request.description }}
              </el-descriptions-item>
              <el-descriptions-item label="Updated At">
                {{ formatDateTime(request.updated_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="Completed At" v-if="request.completed_at">
                {{ formatDateTime(request.completed_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="Admin Comment" :span="2" v-if="request.admin_comment">
                <el-alert :title="request.admin_comment" type="info" :closable="false" />
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <el-empty v-if="requests.length === 0 && !loading" description="No maintenance requests" />
    </el-card>

    <!-- 新建/编辑申请对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? 'Edit Maintenance Request' : 'New Maintenance Request'"
      width="500px" :close-on-click-modal="false">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="Issue Type" prop="issue_type">
          <el-select v-model="form.issue_type" placeholder="Please select issue type" style="width: 100%">
            <el-option label="Plumbing/Electrical" value="水电" />
            <el-option label="Furniture" value="家具" />
            <el-option label="Network" value="网络" />
            <el-option label="Other" value="其他" />
          </el-select>
        </el-form-item>

        <el-form-item label="Description" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="5"
            placeholder="Please describe the issue in detail (10-500 chars)" maxlength="500" show-word-limit />
        </el-form-item>

        <el-form-item label="Priority" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio label="high">High Priority</el-radio>
            <el-radio label="medium">Medium Priority</el-radio>
            <el-radio label="low">Low Priority</el-radio>
          </el-radio-group>
          <div style="color: #909399; font-size: 12px; margin-top: 4px">
            High: urgent issues (e.g., leak, power outage); Medium: normal issues (e.g., broken bulb); Low: can be
            deferred
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? 'Save Changes' : 'Submit Request' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Tools, Plus, Edit, Check, Close, Clock } from '@element-plus/icons-vue'
import { getMaintenanceRequests, createMaintenanceRequest, updateMaintenanceRequest } from '@/api/student'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const requests = ref([])
const formRef = ref(null)
const currentRequestId = ref(null)

const form = reactive({
  issue_type: '',
  description: '',
  priority: 'medium'
})

const rules = {
  issue_type: [
    { required: true, message: 'Please select issue type', trigger: 'change' }
  ],
  description: [
    { required: true, message: 'Please enter issue description', trigger: 'blur' },
    { min: 10, max: 500, message: 'Description length must be between 10 and 500 characters', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: 'Please select priority', trigger: 'change' }
  ]
}

onMounted(() => {
  loadRequests()
})

const loadRequests = async () => {
  try {
    loading.value = true
    const data = await getMaintenanceRequests()
    requests.value = data
  } catch (error) {
    console.error('Failed to load maintenance requests:', error)
  } finally {
    loading.value = false
  }
}

const openDialog = (request = null) => {
  if (request) {
    isEdit.value = true
    currentRequestId.value = request.request_id
    form.issue_type = request.issue_type
    form.description = request.description
    form.priority = request.priority
  } else {
    isEdit.value = false
    currentRequestId.value = null
    form.issue_type = ''
    form.description = ''
    form.priority = 'medium'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    submitting.value = true

    if (isEdit.value) {
      await updateMaintenanceRequest(currentRequestId.value, form)
      ElMessage.success('Maintenance request updated successfully')
    } else {
      await createMaintenanceRequest(form)
      ElMessage.success('Maintenance request submitted successfully')
    }

    dialogVisible.value = false
    await loadRequests()
  } catch (error) {
    if (error !== false) {
      console.error('Operation failed:', error)
    }
  } finally {
    submitting.value = false
  }
}

const getPriorityType = (priority) => {
  const typeMap = {
    'high': 'danger',
    'medium': 'warning',
    'low': 'info'
  }
  return typeMap[priority] || 'info'
}

const getPriorityText = (priority) => {
  const textMap = {
    'high': 'High',
    'medium': 'Medium',
    'low': 'Low'
  }
  return textMap[priority] || priority
}

const getStatusType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled'
  }
  return textMap[status] || status
}

const getTimelineType = (status) => {
  const typeMap = {
    'pending': 'warning',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusIcon = (status) => {
  const iconMap = {
    'pending': Clock,
    'in_progress': Tools,
    'completed': Check,
    'cancelled': Close
  }
  return iconMap[status] || Clock
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('en-US')
}
</script>

<style scoped>
.maintenance-page {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.request-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
