<template>

  <p v-if="loading">Chargement...</p>

  <div v-else class="container">
    <router-link to="/stats" class="u-pull-right">Stats &gt;</router-link>
    <last-updated></last-updated>
    <stats v-bind:trains="trains"></stats>
    <div class="row">
      <train-table id="retour" :trains="trains.retour" :title="infos.to_station + ' ➡️ ' + infos.from_station" anchor="aller"></train-table>
      <train-table id="aller" :trains="trains.aller" :title="infos.from_station + ' ➡️ ' + infos.to_station" anchor="retour"></train-table>
    </div>
  </div>

</template>

<style>
  .refreshing {
    float: left;
    font-size: 0.8em;
    margin-top: 5px;
    color: grey;
  }
  .navigation {
    display: block;
    width: 100%;
    font-size: 0.8em;
    margin-top: -15px;
    margin-bottom: 10px;
  }
</style>

<script>
import TrainTable from './TrainTable'
import LastUpdated from './LastUpdated'
import Stats from './Stats'

export default {
  name: 'timetable',
  components: {
    'train-table': TrainTable,
    'last-updated': LastUpdated,
    'stats': Stats
  },
  data () {
    return {
      loading: true,
      refreshing: false
    }
  },
  computed: {
    trains () {
      return this.$store.state.trains
    },
    infos () {
      return this.$store.state.infos
    }
  },
  created () {
    // initial fetch of trains
    this.$store.dispatch('fetch').then(() => {
      this.loading = false

      // refresh trains periodically
      // `since` arg is handled in the store
      setInterval(() => {
        this.refreshing = true
        this.$store.dispatch('fetch').then(() => {
          this.refreshing = false
        })
      }, 30000)
    })
  }
}
</script>
