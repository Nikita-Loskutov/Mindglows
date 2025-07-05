<script setup>
import { RouterView } from "vue-router";
import NavBar from "./components/NavBar.vue";
import { onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";

onMounted(() => {
  const route = useRoute();
  const router = useRouter();
  if (!route.query.user_id) {
    // Пример для Telegram WebApp JS API
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.initDataUnsafe) {
      const user = window.Telegram.WebApp.initDataUnsafe.user;
      if (user) {
        router.replace({
          path: "/",
          query: {
            user_id: user.id,
            username: user.username || user.first_name || "User"
          }
        });
      }
    }
  }
});
</script>

<template>
  <main>
    
    <RouterView></RouterView>
    <NavBar></NavBar>
  </main>
</template>

<style>
body {
  margin: 0;
  margin-top: 30px;
  font-family: "Arial", sans-serif;
  background: -webkit-linear-gradient(
    90deg,
    #696969,
    #1d1b1d,
    #1d1b1d,
    #8d8688
  );
  background: linear-gradient(90deg, #696969, #1d1b1d, #1d1b1d, #8d8688);
  color: #ffffff;
  display: block;
  justify-content: center;
  align-items: center;
  height: 100%;
}
</style>
