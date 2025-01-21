import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // 监听所有地址
    port: 5173,
    strictPort: false,
    allowedHosts: [
      'localhost',
      '127.0.0.1',
      'icon.mytest.cc',
      // 添加你需要的其他域名
      '.mytest.cc', // 允许所有 mytest.cc 的子域名
    ],
  },
})
