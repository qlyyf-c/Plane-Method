/**
 * Axios HTTP 客户端配置
 *
 * 基础 URL 从环境变量或默认值读取
 * 开发环境:
 *   - VITE_API_BASE_URL 为空 → 使用相对路径 '/api/v1'，通过 Vite 代理转发
 *   - 支持手机等局域网设备访问
 * 生产环境:
 *   - 需要设置 VITE_API_BASE_URL 为实际 API 地址
 */
import axios from 'axios'

// 如果环境变量未设置或为空，使用相对路径（通过 Vite 代理）
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 响应拦截器：统一错误处理
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api