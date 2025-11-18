import request from '@/utils/request'

/**
 * 用户登录
 * @param {string} username - 学号或用户名
 * @param {string} password - 密码
 */
export function login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    return request({
        url: '/auth/login',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

/**
 * 学生注册
 */
export function register(data) {
    return request({
        url: '/auth/register',
        method: 'post',
        data
    })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
    return request({
        url: '/auth/me',
        method: 'get'
    })
}

/**
 * 登出（客户端清除token）
 */
export function logout() {
    return request({
        url: '/auth/logout',
        method: 'post'
    })
}
