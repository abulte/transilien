<template>
  <tr v-bind:class="{canceled: train.type === 'SUPPR'}">
    <td>{{ train.date }}</td>
    <!-- <td>{{ train.num }}</td> -->
    <td v-bind:class="{alert: train.type !== 'NORMAL'}">{{ train.type }}</td>
    <td><span v-if="train.delay">{{ train.delay }}s</span></td>
  </tr>
</template>

<style>
.alert {
  color: rgba(255, 85, 85, 1);
  font-weight: bold;
}
.canceled {
  background-color: rgba(255, 85, 85, 1);
  color: white;
}
.canceled td.alert {
  color: white;
}
</style>

<script>
export default {
  name: 'train-row',
  // TODO validate those types
  props: ['train']
}
</script>
