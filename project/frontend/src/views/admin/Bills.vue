<template>
  <div class="bills-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Tickets /></el-icon>
          <span>账单管理</span>
        </div>
      </template>

      <!-- 筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="宿舍ID">
          <el-input-number v-model="searchForm.dorm_id" :min="1" placeholder="宿舍ID" clearable style="width: 150px" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable style="width: 150px">
            <el-option label="未支付" value="unpaid" />
            <el-option label="已支付" value="paid" />
            <el-option label="已逾期" value="overdue" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 账单列表 -->
      <el-table 
        :data="bills" 
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="bill_id" label="账单ID" width="80" />
        <el-table-column prop="dorm_id" label="宿舍ID" width="80" />
        <el-table-column prop="bill_type" label="类型" width="100" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="{ row }">
            ¥{{ row.amount }}
          </template>
        </el-table-column>
        <el-table-column prop="billing_month" label="账期" width="120" />
        <el-table-column prop="due_date" label="截止日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paid_at" label="支付时间" width="180">
          <template #default="{ row }">
            {{ row.paid_at ? formatDateTime(row.paid_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              v-if="row.status === 'unpaid' || row.status === 'overdue'"
              type="success" 
              size="small" 
              @click="markAsPaid(row)"
            >
              标记已付
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              :icon="Delete"
              @click="handleDelete(row)"
            >
              删除
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
    console.error('加载账单失败:', error)
    ElMessage.error('加载账单失败')
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
    ElMessage.success('已标记为已支付')
    await loadBills()
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error('更新失败')
  }
}

const handleDelete = async (bill) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除账单 ${bill.bill_id} 吗？此操作不可恢复！`,
      '警告',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await deleteBill(bill.bill_id)
    ElMessage.success('账单删除成功')
    await loadBills()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const getStatusType = (status) => {
  const types = { unpaid: 'warning', paid: 'success', overdue: 'danger' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { unpaid: '未支付', paid: '已支付', overdue: '已逾期' }
  return texts[status] || status
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('zh-CN')
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
