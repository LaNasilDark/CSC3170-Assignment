const TOKEN_KEY = 'access_token'
const USER_TYPE_KEY = 'user_type'
const USER_ID_KEY = 'user_id'

export function getToken() {
    return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
    localStorage.removeItem(TOKEN_KEY)
}

export function getUserType() {
    return localStorage.getItem(USER_TYPE_KEY)
}

export function setUserType(userType) {
    localStorage.setItem(USER_TYPE_KEY, userType)
}

export function getUserId() {
    return localStorage.getItem(USER_ID_KEY)
}

export function setUserId(userId) {
    localStorage.setItem(USER_ID_KEY, userId)
}

export function clearAuth() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_TYPE_KEY)
    localStorage.removeItem(USER_ID_KEY)
}

export function setAuthInfo({ access_token, user_type, user_id }) {
    setToken(access_token)
    setUserType(user_type)
    setUserId(user_id)
}
