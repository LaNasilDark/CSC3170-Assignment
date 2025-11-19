<template>
  <div class="dashboard">
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <h2 style="margin: 0 0 20px 0">
          <el-icon style="vertical-align: middle"><Sunny /></el-icon>
          欢迎回来, {{ profile.name || '同学' }}!
        </h2>
      </el-col>
    </el-row>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <!-- 个人信息卡片 -->
      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </div>
          </template>
          <div v-loading="loading.profile">
            <div class="info-item">
              <span class="label">学号:</span>
              <span class="value">{{ profile.student_id }}</span>
            </div>
            <div class="info-item">
              <span class="label">姓名:</span>
              <span class="value">{{ profile.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">学院:</span>
              <span class="value">{{ profile.college }}</span>
            </div>
            <div class="info-item">
              <span class="label">邮箱:</span>
              <span class="value">{{ profile.email }}</span>
            </div>
            <el-button 
              type="primary" 
              link 
              @click="$router.push('/student/profile')"
              style="margin-top: 10px"
            >
              查看详情 →
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 宿舍信息卡片 -->
      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><House /></el-icon>
              <span>宿舍信息</span>
            </div>
          </template>
          <div v-loading="loading.dorm">
            <template v-if="dormitory.building_no">
              <div class="info-item">
                <span class="label">楼栋:</span>
                <span class="value">{{ dormitory.building_no }}</span>
              </div>
              <div class="info-item">
                <span class="label">房间:</span>
                <span class="value">{{ dormitory.room_no }}</span>
              </div>
              <div class="info-item">
                <span class="label">床位:</span>
                <span class="value">
                  {{ dormitory.occupied_beds }}/{{ dormitory.total_beds }}
                  <el-progress 
                    :percentage="(dormitory.occupied_beds / dormitory.total_beds * 100).toFixed(0)" 
                    :stroke-width="6"
                    :show-text="false"
                    style="margin-top: 5px"
                  />
                </span>
              </div>
              <el-button 
                type="primary" 
                link 
                @click="$router.push('/student/dormitory')"
                style="margin-top: 10px"
              >
                查看室友 →
              </el-button>
            </template>
            <el-empty v-else description="暂无宿舍分配" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 账单统计卡片 -->
      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><Wallet /></el-icon>
              <span>待缴账单</span>
            </div>
          </template>
          <div v-loading="loading.bills">
            <div class="bill-stats">
              <div class="stat-item">
                <div class="stat-label">未支付</div>
                <div class="stat-value">{{ unpaidCount }} 笔</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">总金额</div>
                <div class="stat-value amount">¥{{ unpaidAmount }}</div>
              </div>
            </div>
            <el-button 
              type="primary" 
              link 
              @click="$router.push('/student/bills')"
              style="margin-top: 10px"
            >
              查看详情 →
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon><Operation /></el-icon>
          <span>快速操作</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button 
            type="primary" 
            :icon="Sort" 
            @click="$router.push('/student/dorm-change')"
            style="width: 100%"
          >
            申请宿舍调换
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="warning" 
            :icon="Tools" 
            @click="$router.push('/student/maintenance')"
            style="width: 100%"
          >
            提交维修申请
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="success" 
            :icon="Tickets" 
            @click="$router.push('/student/bills')"
            style="width: 100%"
          >
            查看账单
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button 
            type="info" 
            :icon="User" 
            @click="$router.push('/student/profile')"
            style="width: 100%"
          >
            个人信息
          </el-button>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Sunny, User, House, Wallet, Operation, Sort, Tools, Tickets } from '@element-plus/icons-vue'
import { getCurrentUser } from '@/api/auth'
import { getDormitory, getBills } from '@/api/student'

const profile = reactive({
  student_id: '',
  name: '',
  college: '',
  email: ''
})

const dormitory = reactive({
  building_no: '',
  room_no: '',
  occupied_beds: 0,
  total_beds: 0
})

const loading = reactive({
  profile: false,
  dorm: false,
  bills: false
})

const unpaidCount = ref(0)
const unpaidAmount = ref(0)

onMounted(async () => {
  await Promise.all([
    loadProfile(),
    loadDormitory(),
    loadBills()
  ])
})

const loadProfile = async () => {
  try {
    loading.profile = true
    const data = await getCurrentUser()
    Object.assign(profile, data)
  } catch (error) {
    console.error('加载个人信息失败:', error)
  } finally {
    loading.profile = false
  }
}

const loadDormitory = async () => {
  try {
    loading.dorm = true
    const data = await getDormitory()
    Object.assign(dormitory, data)
  } catch (error) {
    console.error('加载宿舍信息失败:', error)
  } finally {
    loading.dorm = false
  }
}

const loadBills = async () => {
  try {
    loading.bills = true
    const data = await getBills({ status: 'unpaid' })
    unpaidCount.value = data.length
    unpaidAmount.value = data.reduce((sum, bill) => sum + parseFloat(bill.amount), 0).toFixed(2)
  } catch (error) {
    console.error('加载账单信息失败:', error)
  } finally {
    loading.bills = false
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.info-card {
  height: 280px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-of-type {
  border-bottom: none;
}

.label {
  color: #909399;
  font-size: 14px;
}

.value {
  color: #303133;
  font-weight: 500;
  font-size: 14px;
}

.bill-stats {
  display: flex;
  justify-content: space-around;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
}

.stat-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 10px;
}

.stat-value {
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.stat-value.amount {
  color: #f56c6c;
}
</style>
