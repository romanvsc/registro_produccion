<template>
  <div id="app">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/items">Items</router-link>
    </nav>
    <router-view />
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  padding: 20px;
}
nav {
  padding: 20px;
  margin-bottom: 20px;
  border-bottom: 1px solid #ccc;
}
nav a {
  margin-right: 15px;
  text-decoration: none;
}
</style>
