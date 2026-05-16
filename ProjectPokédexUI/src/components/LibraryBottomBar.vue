<template>
  <div class="bottom-bar" :class="{ sliding, visible }">
    <svg
      class="bottom-svg"
      viewBox="0 0 393 100"
      preserveAspectRatio="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M6 121H377.873C378.235 121 378.56 120.963 378.861 120.877C381.17 120.217 389.118 117.391 391.803 109.481C391.939 109.08 392 108.634 392 108.161V29.8799C392 29.3815 391.934 28.9187 391.783 28.5088C390.234 24.2937 386.974 22.1683 384.014 21.085C382.534 20.5433 381.148 20.271 380.132 20.1348C379.625 20.0668 379.213 20.0332 378.932 20.0166C378.791 20.0083 378.684 20.0039 378.613 20.002C378.578 20.001 378.552 20.0002 378.536 20H288.158C286.531 20 284.954 19.4328 283.699 18.3965L264.026 2.14551C263.13 1.40526 262.004 1 260.842 1H134.822C133.745 1.00006 132.697 1.34806 131.833 1.99219L109.567 18.6035C108.351 19.5108 106.873 19.9978 105.355 19.9922L6.01855 19.623C3.2499 19.6128 1 21.8544 1 24.623V116C1 118.675 3.10111 120.859 5.74316 120.993L6 121Z"
        fill="#919191"
        stroke="black"
        stroke-width="2"
        vector-effect="non-scaling-stroke"
      />
    </svg>

    <!-- Buttons -->
    <div class="btn-row">
      <LibraryBtn2 class="center-btn" @select="emit('sets')" />
      <LibraryBtn1 class="side-btn" @select="emit('library')" />
      <LibraryBtn3 class="side-btn" @select="emit('scans')" />
    </div>
  </div>
</template>

<script setup>
import LibraryBtn1 from './buttons/LibraryBtn1.vue'
import LibraryBtn2 from './buttons/LibraryBtn2.vue'
import LibraryBtn3 from './buttons/LibraryBtn3.vue'

const emit = defineEmits(['library', 'sets', 'scans'])

defineProps({
  sliding: {
    type: Boolean,
    default: false
  },
  visible: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.bottom-bar {
  position: absolute;
  top: 66px;
  left: -35px;
  width: 100%;
  pointer-events: none;
  z-index: 2;
  transition: left 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94),
              top 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.bottom-bar.sliding {
  left: 0;
}

.bottom-bar.visible {
  top: calc(100% - 100px);
  pointer-events: all;
}

.bottom-svg {
  display: block;
  width: 100%;
  height: 100px;
}

/* Button row sits on top of the SVG, aligned to the three sections */
.btn-row {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  padding: 0 1px;
  align-items:flex-end;
  box-sizing: border-box;
  justify-content: center;
}

.side-btn {
  height: 75%;
  width:100%;
}

.center-btn {
  position: absolute;
  width: 46%;
  height: 100%;
  align-self:flex-start;
}
</style>
