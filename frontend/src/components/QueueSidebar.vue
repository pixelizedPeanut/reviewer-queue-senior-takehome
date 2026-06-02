<script setup lang="ts">
import type { ReviewItem } from "../api";

/**
 * Presentational data properties.
 */
defineProps<{
    items: ReviewItem[];
    selectedId: string | null;
}>();

/**
 * Operational event bubble signals.
 */
defineEmits<{
    (e: "select", id: string): void;
}>();
</script>

<template>
    <aside class="queue-list" aria-label="Review queue">
        <button
            v-for="item in items"
            :key="item.id"
            class="queue-item"
            :class="{ selected: item.id === selectedId }"
            type="button"
            @click="$emit('select', item.id)"
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
</template>

<style scoped>
.queue-list {
    border: 1px solid #d8dee9;
    border-radius: 8px;
    background: #fff;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.queue-item {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
    width: 100%;
    border: 0;
    border-bottom: 1px solid #eef1f6;
    background: transparent;
    padding: 14px;
    text-align: left;
    cursor: pointer;
}

.queue-item:hover,
.queue-item.selected {
    background: #eef5ff;
}

.queue-title {
    color: #162033;
    font-weight: 700;
}

.queue-meta {
    color: #5c6b7e;
    font-size: 13px;
}

@media (max-width: 760px) {
    .queue-list {
        margin-bottom: 16px;
    }
}
</style>
