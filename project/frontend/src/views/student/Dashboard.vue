<template>
  <div class="dashboard">
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <h2 style="margin: 0 0 20px 0">
          <el-icon style="vertical-align: middle">
            <Sunny />
          </el-icon>
          Welcome back, {{ profile.name || 'Student' }}!
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
              <el-icon>
                <User />
              </el-icon>
              <span>Personal Info</span>
            </div>
          </template>
          <div v-loading="loading.profile">
            <div class="info-item">
              <span class="label">Student ID:</span>
              <span class="value">{{ profile.student_id }}</span>
            </div>
            <div class="info-item">
              <span class="label">Name:</span>
              <span class="value">{{ profile.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">College:</span>
              <span class="value">{{ profile.college }}</span>
            </div>
            <div class="info-item">
              <span class="label">Email:</span>
              <span class="value">{{ profile.email }}</span>
            </div>
            <el-button type="primary" link @click="$router.push('/student/profile')" style="margin-top: 10px">
              View Details →
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 宿舍信息卡片 -->
      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon>
                <House />
              </el-icon>
              <span>Dormitory Info</span>
            </div>
          </template>
          <div v-loading="loading.dorm">
            <template v-if="dormitory.building_no">
              <div class="info-item">
                <span class="label">Building:</span>
                <span class="value">{{ dormitory.building_no }}</span>
              </div>
              <div class="info-item">
                <span class="label">Room:</span>
                <span class="value">{{ dormitory.room_no }}</span>
              </div>
              <div class="info-item">
                <span class="label">Beds:</span>
                <span class="value">
                  {{ dormitory.occupied_beds }}/{{ dormitory.total_beds }}
                  <el-progress :percentage="(dormitory.occupied_beds / dormitory.total_beds * 100).toFixed(0)"
                    :stroke-width="6" :show-text="false" style="margin-top: 5px" />
                </span>
              </div>
              <el-button type="primary" link @click="$router.push('/student/dormitory')" style="margin-top: 10px">
                View Roommates →
              </el-button>
            </template>
            <el-empty v-else description="No dormitory assigned" :image-size="60" />
          </div>
        </el-card>
      </el-col>

      <!-- 账单统计卡片 -->
      <el-col :span="8">
        <el-card shadow="hover" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon>
                <Wallet />
              </el-icon>
              <span>Pending Bills</span>
            </div>
          </template>
          <div v-loading="loading.bills">
            <div class="bill-stats">
              <div class="stat-item">
                <div class="stat-label">Unpaid</div>
                <div class="stat-value">{{ unpaidCount }} items</div>
              </div>
              <div class="stat-item">
                <div class="stat-label">Total Amount</div>
                <div class="stat-value amount">¥{{ unpaidAmount }}</div>
              </div>
            </div>
            <el-button type="primary" link @click="$router.push('/student/bills')" style="margin-top: 10px">
              View Details →
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作 -->
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <el-icon>
            <Operation />
          </el-icon>
          <span>Quick Actions</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-button type="primary" :icon="Sort" @click="$router.push('/student/dorm-change')" style="width: 100%">
            Request Dorm Change
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="warning" :icon="Tools" @click="$router.push('/student/maintenance')" style="width: 100%">
            Submit Maintenance Request
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="success" :icon="Tickets" @click="$router.push('/student/bills')" style="width: 100%">
            View Bills
          </el-button>
        </el-col>
        <el-col :span="6">
          <el-button type="info" :icon="User" @click="$router.push('/student/profile')" style="width: 100%">
            Profile
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
    console.error('Failed to load profile:', error)
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
    console.error('Failed to load dormitory info:', error)
  } finally {
    loading.dorm = false
  }
}

const loadBills = async () => {
  try {
    loading.bills = true
    const data = await getBills()
    // 只统计未支付的账单
    const unpaidBills = data.filter(bill => bill.status === 'unpaid')
    unpaidCount.value = unpaidBills.length
    unpaidAmount.value = unpaidBills.reduce((sum, bill) => sum + parseFloat(bill.amount), 0).toFixed(2)
  } catch (error) {
    console.error('Failed to load bills info:', error)
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
