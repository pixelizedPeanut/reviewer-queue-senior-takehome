import { createRouter, createWebHistory } from "vue-router";
import QueueWorkspace from "../views/QueueWorkspace.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "queue-workspace",
      component: QueueWorkspace,
    },
  ],
});

export default router;
