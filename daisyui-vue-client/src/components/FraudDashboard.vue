<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header with subtle shadow and refined branding -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-6 py-5 flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <div class="w-10 h-10 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">N</div>
          <div>
            <h1 class="text-2xl font-semibold text-gray-900">NEXUS</h1>
            <p class="text-sm text-gray-500">Operational Fraud Detection • African Banking</p>
          </div>
        </div>
        <div class="flex items-center space-x-6">
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span class="text-sm text-gray-600">Live • API Connected</span>
          </div>
          <span class="text-xs text-gray-500">Updated just now</span>
        </div>
      </div>
    </header>

    <!-- Stats Cards with improved hierarchy and subtle accents -->
    <div class="max-w-7xl mx-auto px-6 py-8">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow transition-shadow">
          <p class="text-sm font-medium text-gray-600">Total Transactions</p>
          <p class="text-4xl font-bold text-gray-900 mt-4">{{ dashboard.total_transactions.toLocaleString() }}</p>
          <p class="text-xs text-gray-500 mt-4">Today across all channels</p>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow transition-shadow">
          <p class="text-sm font-medium text-gray-600">Flagged Transactions</p>
          <p class="text-4xl font-bold text-orange-600 mt-4">{{ dashboard.flagged_transactions.toLocaleString() }}</p>
          <p class="text-xs text-gray-500 mt-4">Awaiting review</p>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow transition-shadow">
          <p class="text-sm font-medium text-gray-600">Critical Alerts</p>
          <p class="text-4xl font-bold text-red-600 mt-4">{{ dashboard.critical_alerts }}</p>
          <p class="text-xs text-gray-500 mt-4">Require immediate attention</p>
        </div>

        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 hover:shadow transition-shadow">
          <p class="text-sm font-medium text-gray-600">Stolen Checks Detected</p>
          <p class="text-4xl font-bold text-red-700 mt-4">{{ dashboard.stolen_checks_detected }}</p>
          <p class="text-xs text-gray-500 mt-4">This week</p>
        </div>
      </div>
    </div>

    <!-- Tabs with modern underline style -->
    <div class="max-w-7xl mx-auto px-6">
      <div class="border-b border-gray-200">
        <nav class="flex space-x-12">
          <button
            @click="activeTab = 'dashboard'"
            class="py-4 px-1 border-b-4 font-medium text-sm transition-all duration-300"
            :class="activeTab === 'dashboard' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          >
            Dashboard
          </button>
          <button
            @click="activeTab = 'transaction'"
            class="py-4 px-1 border-b-4 font-medium text-sm transition-all duration-300"
            :class="activeTab === 'transaction' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          >
            Analyze Transaction
          </button>
          <button
            @click="activeTab = 'check'"
            class="py-4 px-1 border-b-4 font-medium text-sm transition-all duration-300"
            :class="activeTab === 'check' ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
          >
            Check Verification
          </button>
        </nav>
      </div>
    </div>

    <!-- Dashboard Tab - Recent Alerts -->
    <div v-if="activeTab === 'dashboard'" class="max-w-7xl mx-auto px-6 py-8">
      <div class="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div class="px-8 py-6 border-b border-gray-100 bg-gradient-to-r from-indigo-50 to-transparent">
          <h2 class="text-xl font-semibold text-gray-900">Recent Alerts</h2>
          <p class="text-sm text-gray-600 mt-1">Real-time fraud monitoring activity</p>
        </div>
        <div v-if="loading" class="px-8 py-16 text-center text-gray-500">
          Loading alerts...
        </div>
        <div v-else class="divide-y divide-gray-100">
          <div
            v-for="alert in dashboard.recent_alerts"
            :key="alert.id"
            class="px-8 py-6 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3">
                  <h3 class="font-semibold text-gray-900">{{ alert.alert_type }}</h3>
                  <span
                    class="inline-flex px-3 py-1 text-xs font-medium rounded-full"
                    :class="{
                      'bg-red-100 text-red-700': alert.severity === 'critical',
                      'bg-orange-100 text-orange-700': alert.severity === 'high',
                      'bg-yellow-100 text-yellow-700': alert.severity !== 'critical' && alert.severity !== 'high'
                    }"
                  >
                    {{ alert.severity.toUpperCase() }}
                  </span>
                </div>
                <p class="mt-2 text-sm text-gray-700">{{ alert.details }}</p>
                <p class="mt-3 text-sm text-gray-500">{{ alert.recommendation }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction Analysis Tab -->
    <div v-if="activeTab === 'transaction'" class="max-w-7xl mx-auto px-6 py-8">
      <div class="max-w-3xl">
        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-8">Analyze Transaction</h2>

          <form class="space-y-7" @submit.prevent="analyzeTransaction">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Transaction Amount (KES)</label>
              <input
                v-model.number="transactionForm.amount"
                type="number"
                class="w-full px-5 py-3.5 border border-gray-300 rounded-xl focus:ring-4 focus:ring-indigo-100 focus:border-indigo-600 transition-all"
                placeholder="e.g. 50,000"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Average Transaction Amount (KES)</label>
              <input
                v-model.number="transactionForm.avg_transaction_amount"
                type="number"
                class="w-full px-5 py-3.5 border border-gray-300 rounded-xl focus:ring-4 focus:ring-indigo-100 focus:border-indigo-600 transition-all"
                placeholder="e.g. 1,000"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Transactions in Last 24 Hours</label>
              <input
                v-model.number="transactionForm.transaction_count_24h"
                type="number"
                class="w-full px-5 py-3.5 border border-gray-300 rounded-xl focus:ring-4 focus:ring-indigo-100 focus:border-indigo-600 transition-all"
                placeholder="e.g. 5"
              />
            </div>

            <button
              type="submit"
              :disabled="analyzingTransaction"
              class="w-full py-4 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
            >
              {{ analyzingTransaction ? 'Analyzing Transaction...' : 'Analyze Transaction' }}
            </button>
          </form>

          <!-- Result Card -->
          <div v-if="transactionResult" class="mt-10 p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl border border-gray-200">
            <h3 class="text-xl font-semibold text-gray-900 mb-6">Analysis Result</h3>
            <div class="grid grid-cols-2 gap-6 text-sm">
              <div>
                <p class="text-gray-600">Amount</p>
                <p class="text-2xl font-bold text-gray-900 mt-1">KES {{ transactionResult.amount?.toLocaleString() }}</p>
              </div>
              <div>
                <p class="text-gray-600">Risk Score</p>
                <p class="text-2xl font-bold text-gray-900 mt-1">{{ (transactionResult.risk_score || 0).toFixed(3) }} / 1.000</p>
              </div>
              <div>
                <p class="text-gray-600">Risk Level</p>
                <p class="text-2xl font-bold mt-1"
                  :class="{
                    'text-red-600': transactionResult.risk_level === 'high',
                    'text-yellow-600': transactionResult.risk_level === 'medium',
                    'text-green-600': transactionResult.risk_level === 'low'
                  }"
                >
                  {{ (transactionResult.risk_level || 'low').toUpperCase() }}
                </p>
              </div>
              <div>
                <p class="text-gray-600">Status</p>
                <p class="text-2xl font-bold mt-1" :class="transactionResult.is_flagged ? 'text-red-600' : 'text-green-600'">
                  {{ transactionResult.is_flagged ? 'FLAGGED' : 'APPROVED' }}
                </p>
              </div>
            </div>
            <div v-if="transactionResult.reasons" class="mt-8 pt-8 border-t border-gray-300">
              <p class="text-gray-600 font-medium mb-3">Detected Reasons</p>
              <ul class="space-y-2">
                <li v-for="(reason, i) in transactionResult.reasons" :key="i" class="flex items-start text-gray-700">
                  <span class="text-indigo-600 mr-2">•</span> {{ reason }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Check Verification Tab -->
    <div v-if="activeTab === 'check'" class="max-w-7xl mx-auto px-6 py-8">
      <div class="max-w-3xl">
        <div class="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 class="text-2xl font-semibold text-gray-900 mb-8">Check Verification</h2>

          <form class="space-y-7" @submit.prevent="analyzeCheck">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Check Number</label>
              <input
                v-model="checkForm.check_number"
                type="text"
                class="w-full px-5 py-3.5 border border-gray-300 rounded-xl focus:ring-4 focus:ring-indigo-100 focus:border-indigo-600 transition-all"
                placeholder="e.g. CHK-12345"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Signature Match Score (0–1)</label>
              <input
                v-model.number="checkForm.signature_match_score"
                type="number"
                step="0.01"
                min="0"
                max="1"
                class="w-full px-5 py-3.5 border border-gray-300 rounded-xl focus:ring-4 focus:ring-indigo-100 focus:border-indigo-600 transition-all"
                placeholder="e.g. 0.95"
              />
            </div>

            <div class="space-y-4">
              <label class="flex items-center space-x-4 cursor-pointer">
                <input v-model="checkForm.is_stolen" type="checkbox" class="w-5 h-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500" />
                <span class="text-sm text-gray-700">Reported as stolen</span>
              </label>
              <label class="flex items-center space-x-4 cursor-pointer">
                <input v-model="checkForm.is_duplicate" type="checkbox" class="w-5 h-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500" />
                <span class="text-sm text-gray-700">Duplicate check detected</span>
              </label>
              <label class="flex items-center space-x-4 cursor-pointer">
                <input v-model="checkForm.is_altered" type="checkbox" class="w-5 h-5 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500" />
                <span class="text-sm text-gray-700">Signs of alteration</span>
              </label>
            </div>

            <button
              type="submit"
              :disabled="analyzingCheck"
              class="w-full py-4 px-6 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 text-white font-semibold rounded-xl shadow-md hover:shadow-lg transition-all duration-200"
            >
              {{ analyzingCheck ? 'Verifying Check...' : 'Verify Check' }}
            </button>
          </form>

          <!-- Result Card -->
          <div v-if="checkResult" class="mt-10 p-8 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl border border-gray-200">
            <h3 class="text-xl font-semibold text-gray-900 mb-6">Verification Result</h3>
            <div class="grid grid-cols-2 gap-6 text-sm">
              <div>
                <p class="text-gray-600">Check Number</p>
                <p class="text-2xl font-bold text-gray-900 mt-1">{{ checkResult.check_number }}</p>
              </div>
              <div>
                <p class="text-gray-600">Risk Score</p>
                <p class="text-2xl font-bold text-gray-900 mt-1">{{ (checkResult.risk_score || 0).toFixed(3) }} / 1.000</p>
              </div>
              <div>
                <p class="text-gray-600">Risk Level</p>
                <p class="text-2xl font-bold mt-1"
                  :class="{
                    'text-red-600': ['critical', 'high'].includes(checkResult.risk_level),
                    'text-yellow-600': checkResult.risk_level === 'medium',
                    'text-green-600': !['critical', 'high', 'medium'].includes(checkResult.risk_level)
                  }"
                >
                  {{ (checkResult.risk_level || 'low').toUpperCase() }}
                </p>
              </div>
              <div>
                <p class="text-gray-600">Status</p>
                <p class="text-2xl font-bold mt-1" :class="checkResult.is_flagged ? 'text-red-600' : 'text-green-600'">
                  {{ checkResult.is_flagged ? 'FLAGGED' : 'APPROVED' }}
                </p>
              </div>
            </div>

            <div class="mt-8 pt-8 border-t border-gray-300">
              <p class="text-gray-600 font-medium mb-3">Recommendation</p>
              <p class="text-gray-900">{{ checkResult.recommendation }}</p>
            </div>

            <div v-if="checkResult.fraud_indicators" class="mt-8 pt-8 border-t border-gray-300">
              <p class="text-gray-600 font-medium mb-3">Fraud Indicators</p>
              <ul class="space-y-2">
                <li v-for="(indicator, i) in checkResult.fraud_indicators" :key="i" class="flex items-start text-gray-700">
                  <span class="text-indigo-600 mr-2">•</span> {{ indicator }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FraudDashboard',
  data() {
    return {
      activeTab: 'dashboard',
      loading: true,
      analyzingTransaction: false,
      analyzingCheck: false,
      apiUrl: 'http://localhost:8000',
      
      dashboard: {
        total_transactions: 0,
        flagged_transactions: 0,
        critical_alerts: 0,
        stolen_checks_detected: 0,
        recent_alerts: []
      },
      
      transactionForm: {
        amount: 50000,
        avg_transaction_amount: 1000,
        transaction_count_24h: 5
      },
      transactionResult: null,
      
      checkForm: {
        check_number: '12345',
        signature_match_score: 0.95,
        is_stolen: false,
        is_duplicate: false,
        is_altered: false
      },
      checkResult: null
    }
  },
  
  mounted() {
    this.fetchDashboard()
  },
  
  methods: {
    async fetchDashboard() {
      try {
        this.loading = true
        const response = await fetch(`${this.apiUrl}/api/fraud/dashboard/summary`)
        this.dashboard = await response.json()
      } catch (error) {
        console.error('Error fetching dashboard:', error)
      } finally {
        this.loading = false
      }
    },
    
    async analyzeTransaction() {
      this.analyzingTransaction = true
      try {
        const response = await fetch(`${this.apiUrl}/api/fraud/transactions/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.transactionForm)
        })
        this.transactionResult = await response.json()
      } catch (error) {
        console.error('Error:', error)
        alert('Error analyzing transaction')
      }
      this.analyzingTransaction = false
    },
    
    async analyzeCheck() {
      this.analyzingCheck = true
      try {
        const response = await fetch(`${this.apiUrl}/api/fraud/checks/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.checkForm)
        })
        this.checkResult = await response.json()
      } catch (error) {
        console.error('Error:', error)
        alert('Error analyzing check')
      }
      this.analyzingCheck = false
    }
  }
}
</script>