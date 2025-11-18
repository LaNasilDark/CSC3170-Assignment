import { createRouter, createWebHistory } from 'vue-router'
import { getToken, getUserType } from '@/utils/auth'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/login'
        },
        {
            path: '/login',
            name: 'Login',
            component: () => import('@/views/Login.vue'),
            meta: { public: true }
        },
        {
            path: '/register',
            name: 'Register',
            component: () => import('@/views/Register.vue'),
            meta: { public: true }
        },
        // 学生端路由
        {
            path: '/student',
            component: () => import('@/layouts/StudentLayout.vue'),
            meta: { requiresAuth: true, userType: 'student' },
            children: [
                {
                    path: '',
                    redirect: '/student/dashboard'
                },
                {
                    path: 'dashboard',
                    name: 'StudentDashboard',
                    component: () => import('@/views/student/Dashboard.vue')
                },
                {
                    path: 'profile',
                    name: 'StudentProfile',
                    component: () => import('@/views/student/Profile.vue')
                },
                {
                    path: 'dormitory',
                    name: 'StudentDormitory',
                    component: () => import('@/views/student/Dormitory.vue')
                },
                {
                    path: 'bills',
                    name: 'StudentBills',
                    component: () => import('@/views/student/Bills.vue')
                },
                {
                    path: 'dorm-change',
                    name: 'StudentDormChange',
                    component: () => import('@/views/student/DormChange.vue')
                },
                {
                    path: 'maintenance',
                    name: 'StudentMaintenance',
                    component: () => import('@/views/student/Maintenance.vue')
                }
            ]
        },
        // 管理员端路由
        {
            path: '/admin',
            component: () => import('@/layouts/AdminLayout.vue'),
            meta: { requiresAuth: true, userType: 'admin' },
            children: [
                {
                    path: '',
                    redirect: '/admin/dashboard'
                },
                {
                    path: 'dashboard',
                    name: 'AdminDashboard',
                    component: () => import('@/views/admin/Dashboard.vue')
                },
                {
                    path: 'students',
                    name: 'AdminStudents',
                    component: () => import('@/views/admin/Students.vue')
                },
                {
                    path: 'dormitories',
                    name: 'AdminDormitories',
                    component: () => import('@/views/admin/Dormitories.vue')
                },
                {
                    path: 'dorm-requests',
                    name: 'AdminDormRequests',
                    component: () => import('@/views/admin/DormRequests.vue')
                },
                {
                    path: 'maintenance',
                    name: 'AdminMaintenance',
                    component: () => import('@/views/admin/Maintenance.vue')
                },
                {
                    path: 'bills',
                    name: 'AdminBills',
                    component: () => import('@/views/admin/Bills.vue')
                },
                {
                    path: 'profile',
                    name: 'AdminProfile',
                    component: () => import('@/views/admin/Profile.vue')
                }
            ]
        }
    ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
    const token = getToken()
    const userType = getUserType()

    // 公共页面直接放行
    if (to.meta.public) {
        if (token && (to.path === '/login' || to.path === '/register')) {
            // 已登录用户访问登录/注册页,重定向到对应dashboard
            next(userType === 'student' ? '/student' : '/admin')
        } else {
            next()
        }
        return
    }

    // 需要认证的页面
    if (to.meta.requiresAuth) {
        if (!token) {
            next('/login')
            return
        }

        // 检查用户类型是否匹配
        if (to.meta.userType && to.meta.userType !== userType) {
            next(userType === 'student' ? '/student' : '/admin')
            return
        }
    }

    next()
})

export default router
