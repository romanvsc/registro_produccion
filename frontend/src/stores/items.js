import { defineStore } from 'pinia'
import api from '@/services/api'

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [],
    loading: false,
    error: null
  }),
  
  actions: {
    async fetchItems() {
      this.loading = true
      try {
        const { data } = await api.get('/api/items')
        this.items = data
      } catch (err) {
        this.error = err.message
      } finally {
        this.loading = false
      }
    },
    
    async createItem(item) {
      const { data } = await api.post('/api/items', item)
      this.items.push(data)
      return data
    }
  }
})
