<template>
  <div class="bills-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon>
            <Wallet />
          </el-icon>
          <span>Bills</span>
        </div>
      </template>

      <!-- Filter bar -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="Status Filter">
          <el-radio-group v-model="filterStatus" @change="handleFilter">
            <el-radio-button label="">All</el-radio-button>
            <el-radio-button label="unpaid">Unpaid</el-radio-button>
            <el-radio-button label="paid">Paid</el-radio-button>
            <el-radio-button label="overdue">Overdue</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <!-- Statistics -->
      <el-alert v-if="unpaidStats.count > 0"
        :title="`Unpaid bills: ${unpaidStats.count} items, Total: ¥${unpaidStats.amount}`" type="warning"
        :closable="false" style="margin-bottom: 20px" />

      <!-- Bills list -->
      <el-table :data="bills" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="bill_type" label="Type" width="120">
          <template #default="{ row }">
            <el-tag :type="getBillTypeColor(row.bill_type)">
              {{ row.bill_type }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="amount" label="Amount" width="120">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 600">¥{{ row.amount }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="due_date" label="Due Date" width="120">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
          </template>
        </el-table-column>

        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="payment_date" label="Payment Date" width="120">
          <template #default="{ row }">
            {{ row.paid_at ? formatDate(row.paid_at) : '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="room_no" label="Room No" width="100" />

        <el-table-column prop="created_at" label="Created At" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="pagination">
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 50]"
          :total="total" layout="total, sizes, prev, pager, next, jumper" @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Wallet } from '@element-plus/icons-vue'
import { getBills } from '@/api/student'

const loading = ref(false)
const allBills = ref([]) // 存储所有账单
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// 根据筛选条件过滤账单
const filteredBills = computed(() => {
  if (!filterStatus.value) {
    return allBills.value
  }
  return allBills.value.filter(bill => bill.status === filterStatus.value)
})

// 计算总数
const total = computed(() => filteredBills.value.length)

// 分页后的账单
const bills = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredBills.value.slice(start, end)
})

const unpaidStats = computed(() => {
  const unpaidBills = allBills.value.filter(bill => bill.status === 'unpaid')
  return {
    count: unpaidBills.length,
    amount: unpaidBills.reduce((sum, bill) => sum + parseFloat(bill.amount), 0).toFixed(2)
  }
})

onMounted(() => {
  loadBills()
})

const loadBills = async () => {
  try {
    loading.value = true
    const data = await getBills()
    allBills.value = data
  } catch (error) {
    console.error('Failed to load bills:', error)
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
}

const handleSizeChange = () => {
  currentPage.value = 1
}

const handleCurrentChange = () => {
  // 页码改变时不需要额外操作，computed会自动更新
}

const getBillTypeColor = (type) => {
  const colorMap = {
    '宿舍费': 'primary',
    '水电费': 'success',
    '网络费': 'warning',
    '空调费': 'info'
  }
  return colorMap[type] || ''
}

const getStatusType = (status) => {
  const typeMap = {
    'unpaid': 'warning',
    'paid': 'success',
    'overdue': 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    'unpaid': 'Unpaid',
    'paid': 'Paid',
    'overdue': 'Overdue'
  }
  return textMap[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('en-US')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('en-US')
}
</script>

<style scoped>
.bills-page {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.filter-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
