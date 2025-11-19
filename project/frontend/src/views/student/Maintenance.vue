<template>
  <div class="maintenance-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Tools /></el-icon>
          <span>维修申请管理</span>
          <el-button 
            type="primary" 
            :icon="Plus" 
            @click="openDialog()"
            style="margin-left: auto"
          >
            新建维修申请
          </el-button>
        </div>
      </template>

      <!-- 申请列表 -->
      <el-timeline>
        <el-timeline-item 
          v-for="request in requests" 
          :key="request.request_id"
          :timestamp="formatDateTime(request.created_at)"
          placement="top"
          :type="getTimelineType(request.status)"
          :icon="getStatusIcon(request.status)"
        >
          <el-card>
            <div class="request-header">
              <el-tag :type="getPriorityType(request.priority)" size="large">
                {{ getPriorityText(request.priority) }}优先级
              </el-tag>
              <el-tag :type="getStatusType(request.status)" size="large">
                {{ getStatusText(request.status) }}
              </el-tag>
              <el-button 
                v-if="request.status === 'pending'"
                type="primary" 
                size="small"
                :icon="Edit"
                @click="openDialog(request)"
                style="margin-left: auto"
              >
                编辑
              </el-button>
            </div>

            <el-descriptions :column="2" border style="margin-top: 15px">
              <el-descriptions-item label="问题描述" :span="2">
                {{ request.description }}
              </el-descriptions-item>
              <el-descriptions-item label="提交时间">
                {{ formatDateTime(request.created_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="更新时间">
                {{ formatDateTime(request.updated_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="完成时间" v-if="request.completed_at">
                {{ formatDateTime(request.completed_at) }}
              </el-descriptions-item>
              <el-descriptions-item label="管理员备注" :span="2" v-if="request.admin_comment">
                <el-alert :title="request.admin_comment" type="info" :closable="false" />
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <el-empty v-if="requests.length === 0 && !loading" description="暂无维修申请" />
    </el-card>

    <!-- 新建/编辑申请对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑维修申请' : '新建维修申请'" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form 
        :model="form" 
        :rules="rules" 
        ref="formRef" 
        label-width="100px"
      >
        <el-form-item label="问题描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea" 
            :rows="5"
            placeholder="请详细描述需要维修的问题(10-500字)"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="form.priority">
            <el-radio label="high">高优先级</el-radio>
            <el-radio label="medium">中优先级</el-radio>
            <el-radio label="low">低优先级</el-radio>
          </el-radio-group>
          <div style="color: #909399; font-size: 12px; margin-top: 4px">
            高: 紧急问题(如漏水、断电); 中: 一般问题(如灯泡坏); 低: 可延后问题
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEdit ? '保存修改' : '提交申请' }}
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
  description: '',
  priority: 'medium'
})

const rules = {
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' },
    { min: 10, max: 500, message: '描述长度在10-500字之间', trigger: 'blur' }
  ],
  priority: [
    { required: true, message: '请选择优先级', trigger: 'change' }
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
    console.error('加载维修申请失败:', error)
  } finally {
    loading.value = false
  }
}

const openDialog = (request = null) => {
  if (request) {
    isEdit.value = true
    currentRequestId.value = request.request_id
    form.description = request.description
    form.priority = request.priority
  } else {
    isEdit.value = false
    currentRequestId.value = null
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
      ElMessage.success('维修申请更新成功')
    } else {
      await createMaintenanceRequest(form)
      ElMessage.success('维修申请提交成功')
    }

    dialogVisible.value = false
    await loadRequests()
  } catch (error) {
    if (error !== false) {
      console.error('操作失败:', error)
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
    'high': '高',
    'medium': '中',
    'low': '低'
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
    'pending': '待处理',
    'in_progress': '处理中',
    'completed': '已完成',
    'cancelled': '已取消'
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
  return new Date(dateStr).toLocaleString('zh-CN')
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
