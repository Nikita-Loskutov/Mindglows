import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

const apiserv = 'https://Nikita123543.pythonanywhere.com'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],

  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'https://Nikita123543.pythonanywhere.com', //ВАЖНО ИНАЧЕ ОШИБКУ ВЫДАВАТЬ БУДЕТ//
    ],
    proxy: {
      '/user_data': apiserv,
      '/update_coins': apiserv,
      '/get_card_data': apiserv,
      '/upgrade_card': apiserv,
      '/claim_task_reward': apiserv,
      '/claim_daily_reward': apiserv,
      '/invited_friends': apiserv,
      '/update_profit_per_hour': apiserv,
      '/get_user_cards': apiserv,

    }
  }
})