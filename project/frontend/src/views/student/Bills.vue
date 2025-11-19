<template>
  <div class="bills-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Wallet /></el-icon>
          <span>账单查询</span>
        </div>
      </template>

      <!-- 筛选栏 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="状态筛选">
          <el-radio-group v-model="filterStatus" @change="handleFilter">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="unpaid">未支付</el-radio-button>
            <el-radio-button label="paid">已支付</el-radio-button>
            <el-radio-button label="overdue">逾期</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-form>

      <!-- 统计信息 -->
      <el-alert 
        v-if="unpaidStats.count > 0"
        :title="`未支付账单: ${unpaidStats.count} 笔，总金额: ¥${unpaidStats.amount}`"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px"
      />

      <!-- 账单列表 -->
      <el-table 
        :data="bills" 
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="bill_type" label="账单类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getBillTypeColor(row.bill_type)">
              {{ row.bill_type }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 600">¥{{ row.amount }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="due_date" label="到期日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.due_date) }}
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="payment_date" label="支付日期" width="120">
          <template #default="{ row }">
            {{ row.payment_date ? formatDate(row.payment_date) : '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="description" label="备注" show-overflow-tooltip />

        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Wallet } from '@element-plus/icons-vue'
import { getBills } from '@/api/student'

const loading = ref(false)
const bills = ref([])
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const unpaidStats = computed(() => {
  const unpaidBills = bills.value.filter(bill => bill.status === 'unpaid')
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
    const params = {
      status: filterStatus.value || undefined,
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    const data = await getBills(params)
    bills.value = data
    total.value = data.length // 注意:实际应该从后端返回总数
  } catch (error) {
    console.error('加载账单失败:', error)
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
  loadBills()
}

const handleSizeChange = () => {
  currentPage.value = 1
  loadBills()
}

const handleCurrentChange = () => {
  loadBills()
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
    'unpaid': '未支付',
    'paid': '已支付',
    'overdue': '逾期'
  }
  return textMap[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
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
