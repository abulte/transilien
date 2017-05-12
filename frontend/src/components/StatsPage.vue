<template>
  <p v-if="loading">Chargement...</p>
  <div v-else class="container">
    <router-link to="/">&lt; Accueil</router-link>
    <h4>Derniers trains (2j), par heure</h4>
    <bar-chart :data="chartData('lastHours')" :options="chartOptions" :height="200"></bar-chart>
    <h4>Derniers trains (15j), par jour</h4>
    <bar-chart :data="chartData('lastDays')" :options="chartOptions" :height="200"></bar-chart>
    <h4>Tous les trains, par heure, agrégé</h4>
    <bar-chart :data="chartData('hourOverall')" :options="chartOptions" :height="200"></bar-chart>
    <h4>Tous les trains, par jour de la semaine</h4>
    <bar-chart :data="chartData('weekday')" :options="chartOptions" :height="200"></bar-chart>
    <h4>Tous les trains, par mois</h4>
    <bar-chart :data="chartData('month')" :options="chartOptions" :height="200"></bar-chart>
    <h4>Tous les trains, par jour</h4>
    <bar-chart :data="chartData('day')" :options="chartOptions" :height="200"></bar-chart>
    <!-- <h4>Tous les trains, par an</h4>
    <bar-chart :data="chartData('year')" :options="chartOptions" :height="200"></bar-chart> -->
  </div>
</template>

<script>
import groupBy from 'lodash/groupBy'
import mapValues from 'lodash/mapValues'
import TrainsService from '../services/trains-service'
import BarChart from './charts/Bar'

export default {
  name: 'timetable',
  components: {
    'bar-chart': BarChart
  },
  data() {
    return {
      // stores for the stats
      stats: {
        month: [],
        year: [],
        day: [],
        lastHours: [],
        lastDays: [],
        hourOverall: [],
        weekday: []
      },
      // loading indicator
      loading: true,
      // chartjs chartOptions
      chartOptions: {
        scales: {
          xAxes: [{
            stacked: true,
            barPercentage: 1
          }],
          yAxes: [{
            stacked: true
          }]
        }
      },
      // captions for the chart, by train.type
      types: [{
        name: 'late',
        color: '#ff9849',
        title: 'Retard'
      }, {
        name: 'suppr',
        color: '#ff5555',
        title: 'Supprimé'
      }, {
        name: 'normal',
        color: '#27c795',
        title: 'Normal'
      }],
      // the frequencies we want to fetch and store
      // cf getData()
      frequencies: [{
        name: 'month',
        url: 'month'
      },
      // {
      //   name: 'year',
      //   url: 'year'
      // },
      {
        name: 'day',
        url: 'day'
      }, {
        name: 'hourOverall',
        url: 'hour_overall'
      }, {
        name: 'weekday',
        url: 'weekday'
      }, {
        name:'lastHours',
        url: 'hour',
        since: new Date().setDate(new Date().getDate() - 2) / 1000 | 0
      }, {
        name: 'lastDays',
        url: 'day',
        since: new Date().setDate(new Date().getDate() - 7) / 1000 | 0
      }]
    }
  },
  methods: {
    /**
     * Go from [
     *  {
     *    date: 'X',
     *    type: 'RETARD',
     *    count: 1
     *  }
     * ] to [
     *  {
     *    date: 'X',
     *    values: {
     *      late: 1,
     *      suppr: 0,
     *      normal: 0
     *    }
     *  }
     * ]
     */
    groupStats(stats) {
      let dates = []
      stats.forEach(datum => {
        if (dates.indexOf(datum.date) === -1) {
          dates.push(datum.date)
        }
      })
      return dates.map(date => {
        return {
          date: date,
          values: stats.filter(datum => {
            return datum.date === date
          }).reduce((acc, datum) => {
            return {
              late: datum.type === 'RETARD' ? datum.count : acc.late,
              suppr: datum.type === 'SUPPR' ? datum.count : acc.suppr,
              normal: datum.type === 'NORMAL' ? datum.count : acc.normal
            }
          }, {late: 0, suppr: 0, normal: 0})
        }
      })
    },
    chartData(frequency) {
      let stats = this.stats[frequency]
      if (!stats) {
        console.error('Unknown frequency', frequency)
        return
      }
      let grouped = this.groupStats(stats)
      let datasets = this.types.map(type => {
        return {
          label: type.title,
          backgroundColor: type.color,
          data: grouped.map(group => group.values[type.name])
        }
      })
      let labels
      if (frequency === 'weekday') {
        labels = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
      } else {
        labels = grouped.map(group => group.date.toString().replace(':', 'h'))
      }
      return {
        labels: labels,
        datasets: datasets
      }
    },
    /**
     * Fetch the initial datasets
     * Returns an <Array> of <Promise>
     */
    getData() {
      let promises = []
      this.frequencies.forEach(freq => {
        promises.push(TrainsService.queryAggregate(freq.url, freq.since).then(stats => {
          this.stats[freq.name] = stats
        }))
      })
      return promises
    }
  },
  created() {
    // "dirty" hack to avoid working on undefined data in chartData()
    // better to be reactive?
    Promise.all(this.getData()).then(() => {
      this.loading = false
    })
  }
}
</script>
