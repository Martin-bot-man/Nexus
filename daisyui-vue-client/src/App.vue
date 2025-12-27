<template>
  <FraudDashboard />
</template>

<script>
import FraudDashboard from './components/FraudDashboard.vue'

export default {
  name: 'App',
  components: {
    FraudDashboard
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
}
body {
  background: #0f172a;
}
</style>
