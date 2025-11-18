import request from '@/utils/request'

/**
 * 获取系统统计数据
 */
export function getStatistics() {
    return request({
        url: '/admin/statistics',
        method: 'get'
    })
}

/**
 * 获取学生列表
 */
export function getStudents(params) {
    return request({
        url: '/admin/students',
        method: 'get',
        params
    })
}

/**
 * 获取学生详情
 */
export function getStudentDetail(studentId) {
    return request({
        url: `/admin/students/${studentId}`,
        method: 'get'
    })
}

/**
 * 更新学生信息
 */
export function updateStudent(studentId, data) {
    return request({
        url: `/admin/students/${studentId}`,
        method: 'put',
        data
    })
}

/**
 * 获取宿舍列表
 */
export function getDormitories(params) {
    return request({
        url: '/admin/dormitories',
        method: 'get',
        params
    })
}

/**
 * 获取宿舍入住学生
 */
export function getDormitoryStudents(dormId) {
    return request({
        url: `/admin/dormitories/${dormId}/students`,
        method: 'get'
    })
}

/**
 * 获取宿舍调换申请列表
 */
export function getDormChangeRequests(params) {
    return request({
        url: '/admin/dorm-change-requests',
        method: 'get',
        params
    })
}

/**
 * 处理宿舍调换申请
 */
export function handleDormChangeRequest(requestId, data) {
    return request({
        url: `/admin/dorm-change-requests/${requestId}`,
        method: 'put',
        data
    })
}

/**
 * 获取维修申请列表
 */
export function getMaintenanceRequests(params) {
    return request({
        url: '/admin/maintenance-requests',
        method: 'get',
        params
    })
}

/**
 * 更新维修申请
 */
export function updateMaintenanceRequest(requestId, data) {
    return request({
        url: `/admin/maintenance-requests/${requestId}`,
        method: 'put',
        data
    })
}

/**
 * 获取账单列表
 */
export function getBills(params) {
    return request({
        url: '/admin/bills',
        method: 'get',
        params
    })
}

/**
 * 更新账单状态
 */
export function updateBillStatus(billId, data) {
    return request({
        url: `/admin/bills/${billId}`,
        method: 'put',
        data
    })
}

/**
 * 更新管理员个人信息
 */
export function updateAdminProfile(data) {
    return request({
        url: '/admin/profile',
        method: 'put',
        data
    })
}
