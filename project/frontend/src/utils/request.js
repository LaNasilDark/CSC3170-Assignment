import axios from 'axios'
import { ElMessage } from 'element-plus'
import { getToken, clearAuth } from './auth'
import router from '@/router'

// Create axios instance
const request = axios.create({
    baseURL: '/api', // forwarded to backend via vite proxy
    timeout: 10000
})

// 请求拦截器
request.interceptors.request.use(
    config => {
        const token = getToken()
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    error => {
        console.error('Request error:', error)
        return Promise.reject(error)
    }
)

// 响应拦截器
request.interceptors.response.use(
    response => {
        return response.data
    },
    error => {
        console.error('Response error:', error)

        if (error.response) {
            const { status, data } = error.response

            switch (status) {
                case 401:
                    ElMessage.error('Invalid username or password')
                    clearAuth()
                    router.push('/login')
                    break
                case 403:
                    ElMessage.error('You do not have permission to access')
                    break
                case 404:
                    ElMessage.error('Requested resource not found')
                    break
                case 500:
                    ElMessage.error('Server error')
                    break
                default:
                    ElMessage.error(data?.detail || 'Request failed')
            }
        } else if (error.request) {
            ElMessage.error('Network error, please check your connection')
        } else {
            ElMessage.error('Request configuration error')
        }

        return Promise.reject(error)
    }
)

export default request
