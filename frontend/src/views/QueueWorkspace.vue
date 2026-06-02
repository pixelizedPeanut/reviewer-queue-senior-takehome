<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
    applyReviewAction,
    fetchReviewItems,
    type ReviewAction,
    type ReviewItem,
} from "../api";
import QueueSidebar from "../components/QueueSidebar.vue";
import DetailPanel from "../components/DetailPanel.vue";

const currentReviewer = "alex";
const items = ref<ReviewItem[]>([]);
const selectedId = ref<string | null>(null);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const pendingAction = ref<ReviewAction | null>(null);

/**
 * Computes the active item safely, defaulting to the selected item or
 * falling back to the first item in the list.
 */
const selectedItem = computed(
    () =>
        items.value.find((item) => item.id === selectedId.value) ??
        items.value[0] ??
        null,
);

/**
 * Triggers a network request to load and update the live task queue.
 */
async function loadItems() {
    isLoading.value = true;
    errorMessage.value = null;
    try {
        items.value = await fetchReviewItems();
        selectedId.value = selectedItem.value?.id ?? null;
    } catch (error) {
        errorMessage.value = "Something went wrong loading the queue.";
    } finally {
        isLoading.value = false;
    }
}

/**
 * Submits state transitions to the API and cleanly removes terminal
 * items from the UI view.
 * * @param action - The literal operation flag to execute
 */
async function handleAction(action: ReviewAction) {
    if (!selectedItem.value) return;

    pendingAction.value = action;
    errorMessage.value = null;

    try {
        const updated = await applyReviewAction(
            selectedItem.value.id,
            action,
            currentReviewer,
        );
        const isTerminal = ["approved", "rejected", "escalated"].includes(
            updated.status,
        );

        if (isTerminal) {
            items.value = items.value.filter((item) => item.id !== updated.id);
            selectedId.value = items.value[0]?.id ?? null;
        } else {
            items.value = items.value.map((item) =>
                item.id === updated.id ? updated : item,
            );
        }
    } catch (error: any) {
        errorMessage.value =
            error.response?.data?.detail ||
            "That action could not be completed.";
    } finally {
        pendingAction.value = null;
    }
}

/**
 * Updates the current focused selection ID.
 * * @param id - Target element unique identification token
 */
function handleSelect(id: string) {
    selectedId.value = id;
}

onMounted(loadItems);
</script>

<template>
    <main class="page-shell">
        <header class="topbar">
            <div>
                <p class="eyebrow">Reviewer workspace</p>
                <h1>Active queue ({{ items.length }} items remaining)</h1>
            </div>
            <div class="reviewer">
                Signed in as <strong>{{ currentReviewer }}</strong>
            </div>
        </header>

        <p v-if="errorMessage" class="error-banner">{{ errorMessage }}</p>
        <p v-if="isLoading" class="loading">Loading review items...</p>

        <section v-else class="workspace">
            <QueueSidebar
                :items="items"
                :selected-id="selectedItem?.id ?? null"
                @select="handleSelect"
            />

            <DetailPanel
                :item="selectedItem"
                :current-reviewer="currentReviewer"
                :pending-action="pendingAction"
                @action="handleAction"
            />
        </section>
    </main>
</template>

<style scoped>
.topbar {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 24px;
}

h1 {
    margin-bottom: 0;
    font-size: 34px;
}

.eyebrow {
    margin-bottom: 6px;
    color: #526173;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.reviewer,
.loading,
.error-banner {
    border-radius: 6px;
    padding: 10px 12px;
}

.reviewer {
    background: #e8eef7;
    color: #28364a;
}

.error-banner {
    background: #ffe9e6;
    color: #8b1d0f;
}

.loading {
    background: #fff;
}

.workspace {
    display: grid;
    grid-template-columns: 360px minmax(0, 1fr);
    gap: 20px;
}

@media (max-width: 760px) {
    .topbar,
    .workspace {
        display: block;
    }
}
</style>
