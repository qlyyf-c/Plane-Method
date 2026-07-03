<script setup lang="ts">
/**
 * 关于页面 - 平法助手
 *
 * 功能：
 * - 应用信息展示
 * - 反馈与联系方式
 * - 条文依据声明
 */
const appName = '平法助手 PingFa'
const version = '0.1.0'
const description = '土木工程平法识图辅助学习工具，基于 22G101-1 图集'

// 作者信息（待用户填写）
// const authorName = '待填写'
const contactWechat = '待填写'
const contactEmail = '94784518@qq.com'
</script>

<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mt-4 mb-4">关于 {{ appName }}</h1>
      </v-col>
    </v-row>

    <!-- 应用信息 -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title>应用信息</v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <template v-slot:title>
                  <span class="font-weight-bold">名称</span>
                </template>
                <template v-slot:subtitle>
                  <span>{{ appName }}</span>
                </template>
              </v-list-item>
              <v-list-item>
                <template v-slot:title>
                  <span class="font-weight-bold">版本</span>
                </template>
                <template v-slot:subtitle>
                  <span>{{ version }}</span>
                </template>
              </v-list-item>
              <v-list-item>
                <template v-slot:title>
                  <span class="font-weight-bold">简介</span>
                </template>
                <template v-slot:subtitle>
                  <span>{{ description }}</span>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 反馈与建议 -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title>反馈与建议</v-card-title>
          <v-card-text>
            <p class="text-body-2 mb-3">
              如果您在使用过程中有任何问题、建议或发现 bug，欢迎通过以下方式联系：
            </p>
            <v-list density="compact">
              <v-list-item v-if="contactWechat !== '待填写'">
                <template v-slot:prepend>
                  <v-icon color="success">mdi-wechat</v-icon>
                </template>
                <template v-slot:title>
                  <span class="font-weight-bold">微信</span>
                </template>
                <template v-slot:subtitle>
                  <span>{{ contactWechat }}</span>
                </template>
              </v-list-item>
              <v-list-item v-if="contactEmail !== '待填写'">
                <template v-slot:prepend>
                  <v-icon color="primary">mdi-email</v-icon>
                </template>
                <template v-slot:title>
                  <span class="font-weight-bold">邮箱</span>
                </template>
                <template v-slot:subtitle>
                  <span>{{ contactEmail }}</span>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 条文依据 -->
    <v-row>
      <v-col cols="12">
        <v-card class="mb-4">
          <v-card-title>条文依据</v-card-title>
          <v-card-text>
            <p class="text-body-2">
              本应用计算依据以下规范图集：
            </p>
            <v-list density="compact" class="bg-grey-lighten-4 rounded">
              <v-list-item>
                <template v-slot:title>
                  <span class="font-weight-bold">22G101-1</span>
                </template>
                <template v-slot:subtitle>
                  <span>《混凝土结构施工图平面整体表示方法制图规则和构造详图（现浇混凝土框架、剪力墙、梁、板）》</span>
                </template>
              </v-list-item>
              <v-list-item>
                <template v-slot:title>
                  <span class="font-weight-bold">GB50010-2010</span>
                </template>
                <template v-slot:subtitle>
                  <span>《混凝土结构设计规范》（2015 年版）</span>
                </template>
              </v-list-item>
            </v-list>
            <v-alert type="info" variant="tonal" class="mt-4" density="compact">
              <div class="text-caption">
                <strong>声明：</strong>本应用仅供学习和参考使用，实际工程应用请以最新规范为准，并结合具体工程设计要求。数据内容待进一步校核验证。
              </div>
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

      </v-container>
</template>
