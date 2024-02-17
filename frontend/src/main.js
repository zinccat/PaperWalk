import { createApp } from 'vue'
import App from './App.vue'
import './index.css'
import axios from 'axios'

axios.defaults.baseURL = process.env.VUE_APP_API_URL

createApp(App).mount('#app')
