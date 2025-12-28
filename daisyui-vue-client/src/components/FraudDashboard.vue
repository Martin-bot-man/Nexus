<template>
  <div class="min-h-screen flex flex-col bg-gray-50 text-gray-800 font-sans antialiased">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div class="max-w-[1600px] mx-auto px-6 lg:px-8">
        <div class="h-20 flex items-center justify-between">
          <!-- Logo & Title -->
          <div class="flex items-center space-x-5">
            <div class="flex items-center space-x-4 cursor-pointer">
              <div class="w-12 h-12 bg-gradient-to-br from-indigo-600 to-blue-700 rounded-lg shadow-md flex items-center justify-center text-white text-2xl font-bold">
                N
              </div>
              <div>
                <h1 class="text-2xl font-bold text-gray-900">Nexus</h1>
                <p class="text-xs text-indigo-600 font-semibold uppercase tracking-wide">Africa Core Platform</p>
              </div>
            </div>
          </div>

          <!-- Navigation Tabs - Centered-ish on larger screens -->
          <nav class="hidden lg:flex items-center space-x-1">
            <button
              v-for="tab in tabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                activeTab === tab.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
                'px-6 py-3 rounded-lg text-sm font-medium transition-all duration-200'
              ]"
            >
              {{ tab.name }}
            </button>
          </nav>

          <!-- Right Side Status -->
          <div class="flex items-center space-x-6">
            <!-- Connection Status -->
            <div class="hidden md:flex items-center space-x-3">
              <span class="text-xs font-medium text-gray-500 uppercase tracking-wide">Status</span>
              <div class="flex items-center space-x-2">
                <div :class="wsStatus === 'connected' ? 'bg-green-500' : 'bg-gray-400'" class="w-2.5 h-2.5 rounded-full animate-pulse"></div>
                <span class="text-sm font-medium" :class="wsStatus === 'connected' ? 'text-green-700' : 'text-gray-500'">
                  {{ wsStatus === 'connected' ? 'Live' : 'Disconnected' }}
                </span>
              </div>
            </div>

            <div class="h-10 w-px bg-gray-300 hidden md:block"></div>

            <!-- AI Indicator -->
            <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-sm font-semibold shadow-sm">
              AI
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 max-w-[1600px] w-full mx-auto px-6 lg:px-8 py-12">
      <!-- Key Metrics -->
      <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div
          v-for="stat in stats"
          :key="stat.label"
          class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-300"
        >
          <p class="text-sm font-medium text-gray-600 uppercase tracking-wide">{{ stat.label }}</p>
          <div class="flex items-end justify-between mt-4">
            <p class="text-3xl font-bold text-gray-900 tabular-nums">{{ stat.value }}</p>
            <span class="text-3xl">{{ stat.icon }}</span>
          </div>
          <div class="mt-5">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
              Real-time
            </span>
          </div>
        </div>
      </section>

      <!-- Main Grid Layout -->
      <div class="grid grid-cols-12 gap-8">
        <!-- Fraud Detection Feed -->
        <section class="col-span-12 lg:col-span-8">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-8 py-6 border-b border-gray-200 flex justify-between items-center">
              <div>
                <h2 class="text-xl font-semibold text-gray-900">Fraud Detection Feed</h2>
                <p class="text-sm text-gray-600 mt-1">Live transaction monitoring • Isolation Forest algorithm</p>
              </div>
              <span class="inline-flex items-center px-4 py-2 rounded-lg bg-indigo-50 text-indigo-700 text-xs font-medium border border-indigo-200">
                Model Active • Contamination: 0.05
              </span>
            </div>

            <div class="max-h-[640px] overflow-y-auto divide-y divide-gray-100">
              <TransitionGroup name="list" tag="div">
                <div
                  v-for="event in feed"
                  :key="event.id"
                  class="p-6 hover:bg-gray-50 transition-colors flex items-start space-x-5"
                >
                  <div class="flex-shrink-0 mt-1">
                    <div :class="getRiskColor(event.risk_level)" class="w-4 h-4 rounded-full ring-4 ring-white shadow-lg"></div>
                  </div>

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between mb-2">
                      <p class="text-xs text-gray-500 font-medium">
                        <span class="uppercase">Type:</span> {{ event.type }} •
                        <span class="uppercase">ID:</span> {{ event.id }}
                      </p>
                      <p class="text-xs text-gray-500 font-mono">{{ formatTime(event.timestamp) }}</p>
                    </div>

                    <h3 class="text-base font-medium text-gray-900 mb-3 leading-relaxed">{{ event.reasons[0] }}</h3>

                    <div class="flex flex-wrap gap-2">
                      <span
                        v-for="tag in event.reasons"
                        :key="tag"
                        class="px-3 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-700"
                      >
                        {{ tag }}
                      </span>
                    </div>
                  </div>

                  <div class="text-right">
                    <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">Risk Score</p>
                    <p :class="getRiskTextColor(event.risk_level)" class="text-2xl font-bold tabular-nums">
                      {{ (event.risk_score * 100).toFixed(0) }}%
                    </p>
                  </div>
                </div>
              </TransitionGroup>

              <div v-if="feed.length === 0" class="py-32 text-center">
                <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-6">
                  <svg class="w-8 h-8 text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <p class="text-gray-500 font-medium text-lg">Waiting for transaction stream...</p>
                <p class="text-sm text-gray-400 mt-2">System is synchronizing with live nodes</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Sidebar -->
        <aside class="col-span-12 lg:col-span-4 space-y-8">
          <!-- Internal Audit Status -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
            <h3 class="text-lg font-semibold text-gray-900 mb-2">Internal Audit Status</h3>
            <p class="text-sm text-gray-600 mb-7">Live teller variance & compliance tracking</p>

            <div class="space-y-6">
              <div v-for="i in 5" :key="i" class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                  <div class="w-11 h-11 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-700 text-sm font-semibold shadow-sm">
                    T{{ i }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">Teller Station {{ i }}</p>
                    <p class="text-xs text-gray-500">Branch 00{{ i }} • Nairobi</p>
                  </div>
                </div>
                <div class="flex items-center space-x-4">
                  <div class="w-32 bg-gray-200 rounded-full h-2.5 overflow-hidden">
                    <div
                      class="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all duration-1000 shadow-sm"
                      :style="{ width: tellerProgress[i - 1] + '%' }"
                    ></div>
                  </div>
                  <span class="text-sm font-semibold text-green-700">Compliant</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Geographic Activity -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Geographic Activity</h3>
            <div class="aspect-video bg-gray-100 rounded-xl border-2 border-dashed border-gray-300 flex items-center justify-center">
              <div class="text-center">
                <div class="w-12 h-12 mx-auto mb-3 text-gray-400">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                </div>
                <p class="text-gray-500 font-medium">Map View</p>
                <p class="text-xs text-gray-400 mt-1">Real-time transaction locations across Africa</p>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </main>

    <!-- Footer -->
    <footer class="mt-auto bg-white border-t border-gray-200 py-6">
      <div class="max-w-[1600px] mx-auto px-6 lg:px-8">
        <div class="flex flex-col md:flex-row justify-between items-center text-sm text-gray-600">
          <div class="mb-4 md:mb-0">
            <p>© 2025 Nexus Africa Core. All rights reserved.</p>
          </div>
          <div class="flex items-center space-x-6">
            <a href="#" class="hover:text-indigo-600 transition">Privacy Policy</a>
            <a href="#" class="hover:text-indigo-600 transition">Terms of Service</a>
            <a href="#" class="hover:text-indigo-600 transition">Support</a>
            <span class="text-xs">v2.4.1 • Updated Dec 2025</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const activeTab = ref('alerts')
const wsStatus = ref('disconnected')
const feed = ref([])
const summary = ref({
  transactions_today: 0,
  flagged: 0,
  critical_alerts: 0,
})

const tabs = [
  { id: 'alerts', name: 'Detection Feed' },
  { id: 'transaction', name: 'Transactions' },
  { id: 'teller', name: 'Internal Audit' }
]

const stats = computed(() => [
  { label: 'Transactions Today', value: summary.value.transactions_today.toLocaleString(), icon: '⚡' },
  { label: 'Flagged Events', value: summary.value.flagged, icon: '🛡️' },
  { label: 'Critical Alerts', value: summary.value.critical_alerts, icon: '🚨' },
  { label: 'System Health', value: '99.9%', icon: '✓' }
])

const tellerProgress = [92, 88, 95, 81, 97]

const getRiskColor = (level) => {
  const colors = {
    critical: 'bg-red-500',
    high: 'bg-orange-500',
    medium: 'bg-yellow-500',
    low: 'bg-blue-500'
  }
  return colors[level] || 'bg-green-500'
}

const getRiskTextColor = (level) => {
  const colors = {
    critical: 'text-red-600',
    high: 'text-orange-600',
    medium: 'text-yellow-600'
  }
  return colors[level] || 'text-gray-900'
}

const formatTime = (ts) => ts ? new Date(ts).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '--:--:--'

const fetchSummary = async () => {
  try {
    const res = await fetch('http://localhost:8000/fraud/dashboard/summary')
    if (res.ok) summary.value = await res.json()
  } catch (e) { console.error("API Error:", e) }
}

const connectWebSocket = () => {
  const ws = new WebSocket('ws://localhost:8000/ws/stream')
  ws.onopen = () => wsStatus.value = 'connected'
  ws.onclose = () => {
    wsStatus.value = 'disconnected'
    setTimeout(connectWebSocket, 3000)
  }
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'heartbeat') return
    feed.value.unshift(data)
    if (feed.value.length > 20) feed.value.pop()

    summary.value.transactions_today++
    if (data.is_flagged) summary.value.flagged++
    if (data.risk_level === 'critical') summary.value.critical_alerts++
  }
}

onMounted(() => {
  fetchSummary()
  connectWebSocket()
})
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.45s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}
.list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}
</style>