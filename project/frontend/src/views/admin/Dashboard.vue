<template>
  <div class="dashboard-page">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="学生总数" :value="statistics.total_students">
            <template #prefix>
              <el-icon color="#409EFF"><User /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="宿舍总数" :value="statistics.total_dorms">
            <template #prefix>
              <el-icon color="#67C23A"><House /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="空床位数" :value="statistics.available_beds">
            <template #prefix>
              <el-icon color="#E6A23C"><Position /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <el-statistic title="未付账单" :value="statistics.unpaid_bills">
            <template #prefix>
              <el-icon color="#F56C6C"><Tickets /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待处理事项 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><MessageBox /></el-icon>
              <span>待处理宿舍调换申请</span>
              <el-badge :value="statistics.pending_dorm_changes" class="badge" />
            </div>
          </template>
          <div v-if="statistics.pending_dorm_changes > 0">
            <el-alert
              type="warning"
              :closable="false"
              show-icon
            >
              <template #title>
                有 {{ statistics.pending_dorm_changes }} 个待处理的宿舍调换申请
              </template>
            </el-alert>
            <el-button 
              type="primary" 
              style="margin-top: 15px; width: 100%"
              @click="$router.push('/admin/dorm-requests')"
            >
              前往处理
            </el-button>
          </div>
          <el-empty v-else description="暂无待处理申请" :image-size="100" />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Tools /></el-icon>
              <span>待处理维修申请</span>
              <el-badge :value="statistics.pending_maintenance" class="badge" />
            </div>
          </template>
          <div v-if="statistics.pending_maintenance > 0">
            <el-alert
              type="warning"
              :closable="false"
              show-icon
            >
              <template #title>
                有 {{ statistics.pending_maintenance }} 个待处理的维修申请
              </template>
            </el-alert>
            <el-button 
              type="primary" 
              style="margin-top: 15px; width: 100%"
              @click="$router.push('/admin/maintenance')"
            >
              前往处理
            </el-button>
          </div>
          <el-empty v-else description="暂无待处理申请" :image-size="100" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 性别分布和床位占用率 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><PieChart /></el-icon>
              <span>学生性别分布</span>
            </div>
          </template>
          <div class="gender-stats">
            <div class="gender-item">
              <el-icon :size="30" color="#409EFF"><Male /></el-icon>
              <div class="gender-info">
                <div class="gender-label">男生</div>
                <div class="gender-value">{{ statistics.male_students || 0 }} 人</div>
              </div>
            </div>
            <el-divider direction="vertical" style="height: 60px" />
            <div class="gender-item">
              <el-icon :size="30" color="#F56C6C"><Female /></el-icon>
              <div class="gender-info">
                <div class="gender-label">女生</div>
                <div class="gender-value">{{ statistics.female_students || 0 }} 人</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>宿舍床位占用率</span>
            </div>
          </template>
          <div style="padding: 20px 0">
            <el-progress 
              :percentage="occupancyRate" 
              :color="progressColor"
              :stroke-width="20"
              :text-inside="true"
            />
            <div style="text-align: center; margin-top: 15px; color: #606266">
              已占用 {{ statistics.occupied_beds || 0 }} / {{ statistics.total_beds || 0 }} 个床位
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <el-icon><Operation /></el-icon>
          <span>快捷操作</span>
        </div>
      </template>
      <div class="quick-actions">
        <el-button type="primary" :icon="User" @click="$router.push('/admin/students')">
          学生管理
        </el-button>
        <el-button type="success" :icon="House" @click="$router.push('/admin/dormitories')">
          宿舍管理
        </el-button>
        <el-button type="warning" :icon="MessageBox" @click="$router.push('/admin/dorm-requests')">
          调换审批
        </el-button>
        <el-button type="danger" :icon="Tools" @click="$router.push('/admin/maintenance')">
          维修管理
        </el-button>
        <el-button type="info" :icon="Tickets" @click="$router.push('/admin/bills')">
          账单管理
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  User, House, Position, Tickets, MessageBox, Tools, 
  PieChart, Male, Female, DataAnalysis, Operation 
} from '@element-plus/icons-vue'
import { getStatistics } from '@/api/admin'

const statistics = ref({
  total_students: 0,
  total_dorms: 0,
  available_beds: 0,
  occupied_beds: 0,
  total_beds: 0,
  unpaid_bills: 0,
  pending_dorm_changes: 0,
  pending_maintenance: 0,
  male_students: 0,
  female_students: 0
})

const occupancyRate = computed(() => {
  if (statistics.value.total_beds === 0) return 0
  return Math.round((statistics.value.occupied_beds / statistics.value.total_beds) * 100)
})

const progressColor = computed(() => {
  const rate = occupancyRate.value
  if (rate >= 90) return '#F56C6C'
  if (rate >= 70) return '#E6A23C'
  return '#67C23A'
})

onMounted(() => {
  loadStatistics()
})

const loadStatistics = async () => {
  try {
    const data = await getStatistics()
    statistics.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}
</script>

<style scoped>
.dashboard-page {
  padding: 20px;
}

.stat-card {
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  position: relative;
}

.badge {
  position: absolute;
  right: 0;
}

.gender-stats {
  display: flex;
  justify-content: space-around;
  align-items: center;
  padding: 20px 0;
}

.gender-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.gender-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.gender-label {
  font-size: 14px;
  color: #909399;
}

.gender-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.quick-actions {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.quick-actions .el-button {
  flex: 1;
  min-width: 150px;
}
</style>
