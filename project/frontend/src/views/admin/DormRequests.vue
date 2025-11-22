<template>
  <div class="dorm-requests-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><MessageBox /></el-icon>
          <span>Dorm Change Requests</span>
        </div>
      </template>

      <!-- Filters -->
      <el-radio-group v-model="statusFilter" @change="handleFilterChange" style="margin-bottom: 20px">
        <el-radio-button label="all">All</el-radio-button>
        <el-radio-button label="pending">Pending</el-radio-button>
        <el-radio-button label="approved">Approved</el-radio-button>
        <el-radio-button label="rejected">Rejected</el-radio-button>
      </el-radio-group>

      <!-- 申请列表 -->
      <el-table 
        :data="filteredRequests" 
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="request_id" label="Request ID" width="80" />
        <el-table-column label="Applicant" width="150">
          <template #default="{ row }">
            {{ row.student_name }} ({{ row.student_id }})
          </template>
        </el-table-column>
        <el-table-column label="Current Dorm" width="120">
          <template #default="{ row }">
            {{ row.current_dorm }}
          </template>
        </el-table-column>
        <el-table-column label="Target Dorm" width="120">
          <template #default="{ row }">
            {{ row.target_dorm }}
          </template>
        </el-table-column>
        <el-table-column prop="reason" label="Reason" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Requested At" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <template v-if="row.status === 'pending'">
              <el-button 
                type="success" 
                size="small" 
                :icon="Check"
                @click="handleApprove(row)"
              >
                Approve
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                :icon="Close"
                @click="handleReject(row)"
              >
                Reject
              </el-button>
            </template>
            <el-tag v-else type="info" size="small">Processed</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 审批对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="dialogTitle" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="commentForm" label-width="100px">
        <el-form-item label="Admin Comment">
          <el-input 
            v-model="commentForm.admin_comment" 
            type="textarea"
            :rows="4"
            :placeholder="isApprove ? 'Enter optional approval comment' : 'Enter rejection reason'"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button :type="isApprove ? 'success' : 'danger'" @click="handleSubmit" :loading="submitting">
          {{ isApprove ? 'Confirm Approve' : 'Confirm Reject' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MessageBox, Check, Close } from '@element-plus/icons-vue'
import { getDormChangeRequests, approveDormChange, rejectDormChange } from '@/api/admin'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const requests = ref([])
const statusFilter = ref('all')
const isApprove = ref(true)
const currentRequest = ref(null)

const commentForm = ref({
  admin_comment: ''
})

const dialogTitle = computed(() => {
  return isApprove.value ? 'Approve Request' : 'Reject Request'
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
    const data = await getDormChangeRequests()
    requests.value = data
  } catch (error) {
    console.error('Failed to load requests:', error)
    ElMessage.error('Failed to load requests')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  // 筛选条件改变
}

const handleApprove = (request) => {
  isApprove.value = true
  currentRequest.value = request
  commentForm.value.admin_comment = ''
  dialogVisible.value = true
}

const handleReject = (request) => {
  isApprove.value = false
  currentRequest.value = request
  commentForm.value.admin_comment = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    submitting.value = true

    if (isApprove.value) {
      await approveDormChange(currentRequest.value.request_id, {
        admin_comment: commentForm.value.admin_comment
      })
      ElMessage.success('Request approved')
    } else {
      if (!commentForm.value.admin_comment) {
        ElMessage.warning('Please provide a rejection reason')
        return
      }
      await rejectDormChange(currentRequest.value.request_id, {
        admin_comment: commentForm.value.admin_comment
      })
      ElMessage.success('Request rejected')
    }

    dialogVisible.value = false
    await loadRequests()
  } catch (error) {
    console.error('Operation failed:', error)
    ElMessage.error('Operation failed')
  } finally {
    submitting.value = false
  }
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: 'Pending',
    approved: 'Approved',
    rejected: 'Rejected'
  }
  return texts[status] || status
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  const date = new Date(datetime)
  return date.toLocaleString('en-US')
}
</script>

<style scoped>
.dorm-requests-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}
</style>
