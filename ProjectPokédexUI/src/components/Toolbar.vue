<script>
export default {
  data() {
    return {
      on: {
        slider: true,
        orb: true,
        red: true,
        yellow: true,
        green: true,
      },
    };
  },
  methods: {
    toggle(key) {
      this.on[key] = !this.on[key];
    },
  },
};
</script>

<template>
  <header class="p-0 m-0 w-full h-25 toolbar">
    
  </header>
</template>

<style scoped>
  .toolbar {
    clip-path: polygon(0 0, 100% 0%, 100% 50%, 45% 50%, 35% 100%, 0 100%);
    background-color: gray;
    margin: 0;
    
  }
  
  
</style>
