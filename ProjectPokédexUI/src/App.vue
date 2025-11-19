<script setup>
  import Toolbar from './components/Toolbar.vue'
  import Testview from './views/Testview.vue'
  // ...existing code...
  // new begining 
</script>

<template>
  <!-- ...existing code... -->
  <Toolbar/>
  <div class="pt-16">
    <router-view />
  </div>
  <!-- ...existing code... -->
</template>
