import request from '@/utils/request'

/**
 * 获取学生个人信息
 */
export function getProfile() {
    return request({
        url: '/students/profile',
        method: 'get'
    })
}

/**
 * 更新学生个人信息
 */
export function updateProfile(data) {
    return request({
        url: '/students/profile',
        method: 'put',
        data
    })
}

/**
 * 修改密码
 */
export function changePassword(data) {
    return request({
        url: '/students/password',
        method: 'put',
        data
    })
}

/**
 * 获取宿舍信息
 */
export function getDormitory() {
    return request({
        url: '/students/dormitory',
        method: 'get'
    })
}

/**
 * 获取室友列表
 */
export function getRoommates() {
    return request({
        url: '/students/roommates',
        method: 'get'
    })
}

/**
 * 获取账单列表
 */
export function getBills(params) {
    return request({
        url: '/students/bills',
        method: 'get',
        params
    })
}

/**
 * 获取宿舍调换申请列表
 */
export function getDormChangeRequests() {
    return request({
        url: '/students/dorm-change',
        method: 'get'
    })
}

/**
 * 创建宿舍调换申请
 */
export function createDormChangeRequest(data) {
    return request({
        url: '/students/dorm-change',
        method: 'post',
        data
    })
}

/**
 * 获取维修申请列表
 */
export function getMaintenanceRequests() {
    return request({
        url: '/students/maintenance',
        method: 'get'
    })
}

/**
 * 创建维修申请
 */
export function createMaintenanceRequest(data) {
    return request({
        url: '/students/maintenance',
        method: 'post',
        data
    })
}

/**
 * 更新维修申请（学生只能更新待处理的）
 */
export function updateMaintenanceRequest(id, data) {
    return request({
        url: `/students/maintenance/${id}`,
        method: 'put',
        data
    })
}
