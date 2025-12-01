<script setup>
  import Toolbar from './components/Toolbar.vue'
  import Testview from './views/Testview.vue'
  import APITest from './views/APITest.vue'
  // ...existing code...
  // new begining 
</script>

<template>
  <!-- ...existing code... -->
  <Testview/>
  <div class="pt-16">
    <router-view />
  </div>
  <!-- ...existing code... -->
</template>
