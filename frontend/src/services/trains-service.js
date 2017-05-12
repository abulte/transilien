import Vue from 'vue'

export default {
  query (since) {
    let url = process.env.API_ENDPOINT
    if (since) url += '?since=' + since
    return Vue.http.get(url).then(res => {
      return res.body
    }).catch(err => {
      console.error('Error fetching trains:', err)
    })
  },
  queryAggregate (frequency, since) {
    let url = process.env.API_ENDPOINT + '/aggregate/' + frequency
    if (since) url += '?since=' + since
    return Vue.http.get(url).then(res => {
      return res.body
    }).catch(err => {
      console.error('Error fetching aggregate:', err)
    })
  }
}
