<template>
  <div class="row stats">
    <div class="twelve columns">
      <span class="normal">Normal <span class="number">{{ nbTrainsByType('NORMAL') }}</span></span>
      <span class="suppr">Suppr. <span class="number">{{ nbTrainsByType('SUPPR') }}</span></span>
      <span class="late">Retard <span class="number">{{ nbTrainsByType('RETARD') }}</span></span>
      <span class="total">Total <span class="number">{{ nbTrainsByType() }}</span></span>
      <span class="health">Santé <span class="number">{{ health }}</span>%</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'stats',
  props: ['trains'],
  computed: {
    allTrains() {
      return [...this.trains.aller, ...this.trains.retour]
    },
    health() {
      // (LATE + SUPPR * 2) / (TOTAL + SUPPR)
      let badRatio = (
        this.nbTrainsByType('RETARD') + 2 * this.nbTrainsByType('SUPPR')
      ) / (this.nbTrainsByType() + this.nbTrainsByType('SUPPR'))
      return parseInt((1 - badRatio) * 100)
    }
  },
  methods: {
    nbTrainsByType(type) {
      if (!type) return this.allTrains.length
      return this.allTrains.filter(train => {
        return train.type === type
      }).length
    }
  }
}
</script>

<style>
  @media (max-width: 380px) {
    .stats {
      margin: auto -20px;
    }
    .stats > div > span {
      font-size: 0.7em !important;
    }
  }
  .stats > div {
    margin: 20px auto;
  }
  .stats > div > span {
    font-size: 0.9em;
    padding: 5px;
    border-radius: 5px;
    /*font-weight: bold;*/
    color: white;
  }
  .stats span.suppr {
    background-color: #ff5555;
  }
  .stats span.late {
    background-color: #ff9849;
  }
  .stats span.normal {
    background-color: #27c795;
  }
  .stats span.total {
    background-color: #06C7EA;
  }
  .stats span.health {
    background-color: #D02D81;
  }
  .stats span.number {
    font-weight: bold;
    padding-left: 3px;
  }
</style>
