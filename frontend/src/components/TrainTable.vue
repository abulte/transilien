<template>
  <div class="six columns">
    <h4 v-bind:id="id">{{ title }}</h4>
    <a v-bind:href="anchorLink" class="navigation">{{ anchorText }}</a>
    <table class="pure-table">
        <thead>
          <tr>
            <th>Date</th>
            <!-- <th>Numéro</th> -->
            <th>Circulation</th>
            <th>Retard</th>
          </tr>
        </thead>
        <tbody>
          <train-row v-for="train in trains" v-bind:train="train"></train-row>
        </tbody>
    </table>
  </div>
</template>

<script>
import TrainRow from './TrainRow'

export default {
  name: 'train-table',
  computed: {
    anchorLink () {
      return '#' + this.anchor
    },
    anchorText () {
      return this.anchor.charAt(0).toUpperCase() + this.anchor.slice(1)
    }
  },
  components: {
    'train-row': TrainRow
  },
  // TODO validate those types
  props: ['title', 'trains', 'anchor', 'id'],
}
</script>
