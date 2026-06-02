<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
    applyReviewAction,
    fetchReviewItems,
    type ReviewAction,
    type ReviewItem,
} from "./api";

const currentReviewer = "alex";
const items = ref<ReviewItem[]>([]);
const selectedId = ref<string | null>(null);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const pendingAction = ref<ReviewAction | null>(null);

// Computes the active item safely
const selectedItem = computed(
    () =>
        items.value.find((item) => item.id === selectedId.value) ??
        items.value[0] ??
        null,
);

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

async function performAction(action: ReviewAction) {
    if (!selectedItem.value) return;

    pendingAction.value = action;
    errorMessage.value = null;

    try {
        // 1. Fire API Action
        const updated = await applyReviewAction(
            selectedItem.value.id,
            action,
            currentReviewer,
        );

        // TAKEHOME: Explicit Product Rule Optimization
        // Since 'approved', 'rejected', and 'escalated' are terminal states, the active queue must exclude them.
        // We instantly strip the item out of the UI list if it enters a terminal state, or update it if it's 'in_review'.
        const isTerminal = ["approved", "rejected", "escalated"].includes(
            updated.status,
        );

        if (isTerminal) {
            items.value = items.value.filter((item) => item.id !== updated.id);
            // Auto-select the next available item in the filtered list
            selectedId.value = items.value[0]?.id ?? null;
        } else {
            items.value = items.value.map((item) =>
                item.id === updated.id ? updated : item,
            );
        }
    } catch (error: any) {
        // Catch custom backend 400 violations safely
        errorMessage.value =
            error.response?.data?.detail ||
            "That action could not be completed.";
    } finally {
        pendingAction.value = null;
    }
}

function formatDate(value: string) {
    return new Intl.DateTimeFormat("en-GB", {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(new Date(value));
}

// TAKEHOME PRODUCT ENGINE: Dynamic Workflow Enforcers
const canClaim = computed(() => selectedItem.value?.status === "unassigned");
const canProcess = computed(() => selectedItem.value?.status === "in_review");

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
            <aside class="queue-list" aria-label="Review queue">
                <button
                    v-for="item in items"
                    :key="item.id"
                    class="queue-item"
                    :class="{ selected: item.id === selectedItem?.id }"
                    type="button"
                    @click="selectedId = item.id"
                >
                    <span class="queue-title">{{ item.title }}</span>
                    <span class="queue-meta">
                        <span :class="['badge-risk', item.risk_level]"
                            >{{ item.risk_level.toUpperCase() }} Risk</span
                        >
                        ·
                        <span :class="['badge-tier', item.customer_tier]">{{
                            item.customer_tier
                        }}</span>
                    </span>
                    <span class="queue-meta">
                        Status: <strong>{{ item.status }}</strong> · Assignee:
                        {{ item.assigned_reviewer ?? "unassigned" }}
                    </span>
                </button>
            </aside>

            <section v-if="selectedItem" class="detail-panel">
                <div class="detail-header">
                    <div>
                        <p class="eyebrow">Item ID: {{ selectedItem.id }}</p>
                        <h2>{{ selectedItem.title }}</h2>
                    </div>
                    <span :class="['status-pill', selectedItem.status]">{{
                        selectedItem.status
                    }}</span>
                </div>

                <div
                    v-if="selectedItem.assigned_reviewer"
                    class="ownership-banner"
                >
                    🔒 Locked by:
                    <strong>{{ selectedItem.assigned_reviewer }}</strong>
                    <span
                        v-if="
                            selectedItem.assigned_reviewer === currentReviewer
                        "
                    >
                        (You)</span
                    >
                </div>

                <dl class="facts">
                    <div>
                        <dt>Submitted</dt>
                        <dd>{{ formatDate(selectedItem.submitted_at) }}</dd>
                    </div>
                    <div>
                        <dt>Risk Level</dt>
                        <dd>{{ selectedItem.risk_level }}</dd>
                    </div>
                    <div>
                        <dt>Customer Account</dt>
                        <dd>{{ selectedItem.customer_tier }}</dd>
                    </div>
                    <div>
                        <dt>Current Assignee</dt>
                        <dd>
                            {{ selectedItem.assigned_reviewer ?? "Unassigned" }}
                        </dd>
                    </div>
                </dl>

                <p class="summary">{{ selectedItem.summary }}</p>
                <p class="notes">
                    {{ selectedItem.notes_count }} operational notes on this
                    item
                </p>

                <div class="actions" aria-label="Workflow actions">
                    <button
                        type="button"
                        :disabled="Boolean(pendingAction) || !canClaim"
                        @click="performAction('claim')"
                    >
                        {{
                            pendingAction === "claim"
                                ? "Claiming..."
                                : "Claim Task"
                        }}
                    </button>

                    <button
                        type="button"
                        :disabled="Boolean(pendingAction) || !canProcess"
                        @click="performAction('approve')"
                        class="btn-approve"
                    >
                        Approve
                    </button>

                    <button
                        type="button"
                        :disabled="Boolean(pendingAction) || !canProcess"
                        @click="performAction('reject')"
                        class="btn-reject"
                    >
                        Reject
                    </button>

                    <button
                        type="button"
                        :disabled="Boolean(pendingAction) || !canProcess"
                        @click="performAction('escalate')"
                        class="btn-escalate"
                    >
                        Escalate
                    </button>
                </div>
            </section>
        </section>
    </main>
</template>
