<template>
  <div class="dormitory-page">
    <el-row :gutter="20">
      <!-- 宿舍信息 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon>
                <House />
              </el-icon>
              <span>Dormitory Info</span>
            </div>
          </template>
          <div v-loading="loading">
            <template v-if="dormitory.building_no">
              <div class="dorm-info">
                <el-descriptions :column="1" border>
                  <el-descriptions-item label="Building">
                    <el-tag type="primary">{{ dormitory.building_no }}</el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="Floor">
                    {{ dormitory.floor_no }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Room No">
                    {{ dormitory.room_no }}
                  </el-descriptions-item>
                  <el-descriptions-item label="Gender Type">
                    <el-tag :type="dormitory.gender_type === '男' ? 'primary' : 'danger'">
                      {{ dormitory.gender_type }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="Bed Occupancy">
                    <div>
                      <div style="margin-bottom: 8px">
                        <span style="font-size: 18px; font-weight: 600; color: #409eff">
                          {{ dormitory.occupied_beds }}
                        </span>
                        <span style="color: #909399"> / {{ dormitory.total_beds }} 床</span>
                      </div>
                      <el-progress :percentage="bedOccupancyRate" :color="getBedProgressColor(bedOccupancyRate)"
                        :stroke-width="12" />
                    </div>
                  </el-descriptions-item>
                  <el-descriptions-item label="Available Beds">
                    <el-tag :type="availableBeds > 0 ? 'success' : 'info'">
                      {{ availableBeds }} available beds
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>

                <!-- 床位可视化 -->
                <div class="bed-visual" style="margin-top: 20px">
                  <div class="bed-title">Bed Layout</div>
                  <div class="beds-container">
                    <div v-for="i in dormitory.total_beds" :key="i"
                      :class="['bed-item', i <= dormitory.occupied_beds ? 'occupied' : 'empty']">
                      <el-icon :size="30">
                        <CircleCheckFilled v-if="i <= dormitory.occupied_beds" />
                        <CircleClose v-else />
                      </el-icon>
                      <div class="bed-label">{{ i <= dormitory.occupied_beds ? 'Occupied' : 'Available' }}</div>
                      </div>
                    </div>
                  </div>
                </div>
            </template>
            <el-empty v-else description="No dormitory assigned" />
          </div>
        </el-card>
      </el-col>

      <!-- 室友列表 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon>
                <User />
              </el-icon>
              <span>Roommates</span>
            </div>
          </template>
          <div v-loading="loading">
            <template v-if="roommates.length > 0">
              <div v-for="(roommate, index) in roommates" :key="roommate.student_id" class="roommate-item">
                <el-avatar :size="50" :style="{ backgroundColor: getAvatarColor(index) }">
                  {{ roommate.name?.charAt(0) }}
                </el-avatar>
                <div class="roommate-info">
                  <div class="roommate-name">
                    {{ roommate.name }}
                    <el-tag v-if="roommate.student_id === currentStudentId" type="success" size="small">
                      Me
                    </el-tag>
                  </div>
                  <div class="roommate-details">
                    <el-tag size="small" effect="plain">{{ roommate.student_id }}</el-tag>
                    <el-tag size="small" type="info" effect="plain">{{ roommate.college }}</el-tag>
                    <el-tag size="small" type="warning" effect="plain">Class of {{ roommate.enrollment_year }}</el-tag>
                  </div>
                </div>
              </div>
            </template>
            <el-empty v-else description="No roommates" :image-size="100" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { House, User, CircleCheckFilled, CircleClose } from '@element-plus/icons-vue'
import { getDormitory, getRoommates } from '@/api/student'
import { getUserId } from '@/utils/auth'

const loading = ref(false)
const currentStudentId = ref('')

const dormitory = reactive({
  building_no: '',
  floor_no: null,
  room_no: '',
  gender_type: '',
  total_beds: 0,
  occupied_beds: 0
})

const roommates = ref([])

const bedOccupancyRate = computed(() => {
  if (dormitory.total_beds === 0) return 0
  return Math.round((dormitory.occupied_beds / dormitory.total_beds) * 100)
})

const availableBeds = computed(() => {
  return dormitory.total_beds - dormitory.occupied_beds
})

onMounted(async () => {
  currentStudentId.value = getUserId()
  await Promise.all([
    loadDormitory(),
    loadRoommates()
  ])
})

const loadDormitory = async () => {
  try {
    loading.value = true
    const data = await getDormitory()
    if (data && data.dorm_id) {
      Object.assign(dormitory, data)
    }
  } catch (error) {
    console.error('Failed to load dormitory info:', error)
    // 如果是404错误(未分配宿舍),不显示错误提示
    if (error.response?.status !== 404) {
      ElMessage.error('Failed to load dormitory info')
    }
  } finally {
    loading.value = false
  }
}

const loadRoommates = async () => {
  try {
    const data = await getRoommates()
    roommates.value = data || []
  } catch (error) {
    console.error('Failed to load roommates list:', error)
    // 404错误表示未分配宿舍,不显示错误
    if (error.response?.status !== 404) {
      ElMessage.error('Failed to load roommates list')
    }
  }
}

const getBedProgressColor = (percentage) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

const getAvatarColor = (index) => {
  const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399']
  return colors[index % colors.length]
}
</script>

<style scoped>
.dormitory-page {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.dorm-info {
  padding: 0;
}

.bed-title {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 12px;
}

.beds-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}

.bed-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px;
  border-radius: 8px;
  border: 2px solid;
  transition: all 0.3s;
}

.bed-item.occupied {
  background-color: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.bed-item.empty {
  background-color: #f5f7fa;
  border-color: #dcdfe6;
  color: #909399;
}

.bed-label {
  margin-top: 4px;
  font-size: 12px;
}

.roommate-item {
  display: flex;
  align-items: center;
  padding: 15px;
  margin-bottom: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.roommate-item:hover {
  background-color: #ecf5ff;
  transform: translateX(4px);
}

.roommate-item:last-child {
  margin-bottom: 0;
}

.roommate-info {
  flex: 1;
  margin-left: 15px;
}

.roommate-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.roommate-details {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
