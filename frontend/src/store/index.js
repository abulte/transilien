import Vue from 'vue'
import Vuex from 'vuex'
import unionBy from 'lodash/unionBy'

import TrainsService from '../services/trains-service'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    infos: {},
    trains: {
      aller: [],
      retour: []
    },
    lastHistoryDate: undefined,
    lastUpdated: undefined
  },
  mutations: {
    add (state, trains) {
      if (trains.aller.length) {
        // merge arrays by id, new trains should replace existing ones
        state.trains.aller = unionBy(trains.aller, state.trains.aller, 'id')
        // force state "refresh" by created a new object
        state.trains.aller = [...state.trains.aller]
      }
      if (trains.retour.length) {
        // merge arrays by id, new trains should replace existing ones
        state.trains.retour = unionBy(trains.retour, state.trains.retour, 'id')
        // force state "refresh" by created a new object
        state.trains.retour = [...state.trains.retour]
      }
      state.infos = trains.infos
    },
    recordLastUpdated (state) {
      state.lastUpdated = Date.now() / 1000 | 0
    }
  },
  actions: {
    fetch (context) {
      return TrainsService.query(context.state.lastUpdated).then((trains) => {
        context.commit('add', trains)
        context.commit('recordLastUpdated')
      })
    }
  }
})
