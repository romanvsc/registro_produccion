<template>
  <div>
    <h1>Items</h1>
    <button @click="fetchItems">Refresh</button>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <ul v-else>
      <li v-for="item in items" :key="item.id">
        {{ item.name }} - {{ item.description }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { useItemsStore } from '@/stores/items'
import { onMounted } from 'vue'

const itemsStore = useItemsStore()
const { items, loading, error } = storeToRefs(itemsStore)
const { fetchItems } = itemsStore

onMounted(() => {
  fetchItems()
})
</script>
