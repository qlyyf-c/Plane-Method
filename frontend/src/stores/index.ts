/**
 * Pinia Store 入口 - 平法助手
 *
 * 当前为空壳，后续 Week 2-5 根据功能需求添加：
 * - useAnchorStore（锚固计算状态）
 * - useAnnotationStore（标注解析状态）
 * - useHistoryStore（最近查询记录）
 */
import { defineStore } from 'pinia'

// 空壳 store，后续扩展
export const useAppStore = defineStore('app', {
  state: () => ({
    appName: '平法助手 PingFa',
    version: '0.1.0'
  }),
  getters: {},
  actions: {}
})