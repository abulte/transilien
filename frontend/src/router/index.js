import Vue from 'vue'
import Router from 'vue-router'
import Timetable from 'components/Timetable'
import StatsPage from 'components/StatsPage'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Timetable',
      component: Timetable
    },
    {
      path: '/stats',
      name: 'StatsPage',
      component: StatsPage
    }
  ],
  // let the html5 anchors work
  mode: 'history'
})
