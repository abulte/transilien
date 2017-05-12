<template>
  <div id="app">
    <!-- <img src="./assets/logo.png"> -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'app'
}
</script>

<style>
  h4, p, .columns {
    text-align: center;
  }
  .description {
    font-size: 0.8em;
  }
  .pure-table {
    margin-left: auto;
    margin-right: auto;
  }
  .container {
    width: 100%;
  }
  @media (max-width: 925px) {
    .six.columns {
      width: 100%;
      margin-left: 0;
    }
  }
</style>
