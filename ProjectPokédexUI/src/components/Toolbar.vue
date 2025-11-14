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
  <header class="w-full h-25 toolbar">
    
  </header>
</template>

<style scoped>
  .toolbar {
    clip-path: polygon(0 0, 100% 0, 100% 100%, 0 100%);
    background-color: gray;
  }

  
</style>
