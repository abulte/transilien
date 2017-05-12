<template>
  <div class="pure-u-1 refreshing">Mise à jour il y a {{ lastUpdatedSeconds }} sec.</div>
</template>

<script>
export default {
  name: 'last-updated',
  data () {
    return {
      lastUpdatedSeconds: 0
    }
  },
  computed: {
    lastUpdated() {
      return this.$store.state.lastUpdated
    }
  },
  created() {
    // update lastUpdatedSeconds counter every second
    setInterval(() => {
      if (!this.lastUpdated) return
      this.lastUpdatedSeconds = (Date.now() / 1000 | 0) - this.lastUpdated
    }, 1000)
  }
}
</script>
