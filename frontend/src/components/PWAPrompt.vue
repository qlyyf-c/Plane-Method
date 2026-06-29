<template>
  <v-snackbar
    v-model="showSnackbar"
    :timeout="-1"
    location="bottom"
    class="pwa-snackbar"
  >
    <div class="d-flex align-center">
      <v-icon
        :icon="offlineReady ? 'mdi-check-circle' : 'mdi-sync'"
        :color="offlineReady ? 'success' : 'info'"
        class="mr-2"
      />
      <span>{{ message }}</span>
    </div>
    <template v-slot:actions>
      <v-btn
        v-if="needRefresh"
        color="primary"
        variant="text"
        @click="handleUpdate"
        :loading="updating"
      >
        更新
      </v-btn>
      <v-btn
        color="grey"
        variant="text"
        @click="handleClose"
      >
        关闭
      </v-btn>
    </template>
  </v-snackbar>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { usePWA } from '../composables/usePWA'

const { needRefresh, offlineReady, close, updateApp } = usePWA()
const updating = ref(false)

const showSnackbar = computed(() => needRefresh.value || offlineReady.value)

const message = computed(() => {
  if (needRefresh.value) {
    return '发现新版本，点击更新获取最新功能'
  }
  if (offlineReady.value) {
    return '应用已缓存，离线也可使用'
  }
  return ''
})

const handleUpdate = async () => {
  updating.value = true
  await updateApp()
  updating.value = false
}

const handleClose = () => {
  close()
}

// 离线就绪提示自动关闭
watch(offlineReady, (val) => {
  if (val) {
    setTimeout(() => {
      close()
    }, 3000)
  }
})
</script>

<style scoped>
.pwa-snackbar {
  margin-bottom: 56px; /* 留出底部导航栏空间 */
}
</style>
