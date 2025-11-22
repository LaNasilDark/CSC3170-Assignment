<template>
  <div class="bills-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Tickets /></el-icon>
          <span>Bills Management</span>
        </div>
      </template>

      <!-- Filters -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="Dorm ID">
          <el-input-number v-model="searchForm.dorm_id" :min="1" placeholder="Dorm ID" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="searchForm.status" placeholder="Select status" clearable style="width: 150px">
            <el-option label="Unpaid" value="unpaid" />
            <el-option label="Paid" value="paid" />
            <el-option label="Overdue" value="overdue" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">Search</el-button>
          <el-button :icon="Refresh" @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>

      <!-- 账单列表 -->
      <el-table 
        :data="bills" 
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="bill_id" label="Bill ID" width="80" />
        <el-table-column prop="dorm_id" label="Dorm ID" width="80" />
        <el-table-column prop="bill_type" label="Type" width="100" />
        <el-table-column prop="amount" label="Amount" width="100">
          <template #default="{ row }">
            ¥{{ row.amount }}
          </template>
        </el-table-column>
        <el-table-column prop="billing_month" label="Billing Month" width="120" />
        <el-table-column prop="due_date" label="Due Date" width="120" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="Paid At" width="180">
          <template #default="{ row }">
            {{ row.paid_at ? formatDateTime(row.paid_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'unpaid' || row.status === 'overdue'"
              type="success" 
              size="small" 
              @click="markAsPaid(row)"
            >
              Mark Paid
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
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Tickets, Search, Refresh, Delete } from '@element-plus/icons-vue'
import { getBills, updateBillStatus, deleteBill } from '@/api/admin'

const loading = ref(false)
const bills = ref([])

const searchForm = reactive({
  dorm_id: null,
  status: ''
})

onMounted(() => {
  loadBills()
})

const loadBills = async () => {
  try {
    loading.value = true
    // 将前端参数映射到后端期望的参数名
    const params = {}
    if (searchForm.dorm_id) params.dorm_id = searchForm.dorm_id
    if (searchForm.status) params.status_filter = searchForm.status
    
    const data = await getBills(params)
    // 处理后端返回的分页格式
    if (data.items) {
      bills.value = data.items
    } else if (Array.isArray(data)) {
      bills.value = data
    } else {
      bills.value = []
    }
    } catch (error) {
    console.error('Failed to load bills:', error)
    ElMessage.error('Failed to load bills')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadBills()
}

const handleReset = () => {
  searchForm.dorm_id = null
  searchForm.status = ''
  loadBills()
}

const markAsPaid = async (bill) => {
  try {
    // 后端期望 new_status 作为 query 参数
    await updateBillStatus(bill.bill_id, 'paid')
    ElMessage.success('Marked as paid')
    await loadBills()
  } catch (error) {
    console.error('Update failed:', error)
    ElMessage.error('Update failed')
  }
}

const handleDelete = async (bill) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete bill ${bill.bill_id}? This action cannot be undone!`,
      'Warning',
      { confirmButtonText: 'Confirm', cancelButtonText: 'Cancel', type: 'warning' }
    )
    await deleteBill(bill.bill_id)
    ElMessage.success('Bill deleted')
    await loadBills()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete failed:', error)
      ElMessage.error('Delete failed')
    }
  }
}

const getStatusType = (status) => {
  const types = { unpaid: 'warning', paid: 'success', overdue: 'danger' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { unpaid: 'Unpaid', paid: 'Paid', overdue: 'Overdue' }
  return texts[status] || status
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('en-US')
}
</script>

<style scoped>
.bills-page {
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
