<script setup lang="ts">
import { computed } from "vue";
import type { ReviewItem, ReviewAction } from "../api";

/**
 * Presentational data properties.
 */
const props = defineProps<{
    item: ReviewItem | null;
    currentReviewer: string;
    pendingAction: ReviewAction | null;
}>();

/**
 * Operational event bubble signals.
 */
defineEmits<{
    (e: "action", action: ReviewAction): void;
}>();

/**
 * Validates if the selected task is available to be claimed.
 */
const canClaim = computed(() => props.item?.status === "unassigned");

/**
 * Validates if the selected task is locked and available to be processed.
 */
const canProcess = computed(() => props.item?.status === "in_review");

/**
 * Converts standard string date payloads cleanly into a local string format.
 * * @param value - ISO String representation of date arrays
 * @returns Formatted representation matching regional style strings
 */
function formatDate(value: string) {
    return new Intl.DateTimeFormat("en-GB", {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(new Date(value));
}
</script>

<template>
    <section v-if="item" class="detail-panel">
        <div class="detail-header">
            <div>
                <p class="eyebrow">Item ID: {{ item.id }}</p>
                <h2>{{ item.title }}</h2>
            </div>
            <span :class="['status-pill', item.status]">{{ item.status }}</span>
        </div>

        <div v-if="item.assigned_reviewer" class="ownership-banner">
            🔒 Locked by: <strong>{{ item.assigned_reviewer }}</strong>
            <span v-if="item.assigned_reviewer === currentReviewer">
                (You)</span
            >
        </div>

        <dl class="facts">
            <div>
                <dt>Submitted</dt>
                <dd>{{ formatDate(item.submitted_at) }}</dd>
            </div>
            <div>
                <dt>Risk Level</dt>
                <dd>{{ item.risk_level }}</dd>
            </div>
            <div>
                <dt>Customer Account</dt>
                <dd>{{ item.customer_tier }}</dd>
            </div>
            <div>
                <dt>Current Assignee</dt>
                <dd>{{ item.assigned_reviewer ?? "Unassigned" }}</dd>
            </div>
        </dl>

        <p class="summary">{{ item.summary }}</p>
        <p class="notes">
            {{ item.notes_count }} operational notes on this item
        </p>

        <div class="actions" aria-label="Workflow actions">
            <button
                type="button"
                :disabled="Boolean(pendingAction) || !canClaim"
                @click="$emit('action', 'claim')"
            >
                {{ pendingAction === "claim" ? "Claiming..." : "Claim Task" }}
            </button>

            <button
                type="button"
                :disabled="Boolean(pendingAction) || !canProcess"
                @click="$emit('action', 'approve')"
                class="btn-approve"
            >
                Approve
            </button>

            <button
                type="button"
                :disabled="Boolean(pendingAction) || !canProcess"
                @click="$emit('action', 'reject')"
                class="btn-reject"
            >
                Reject
            </button>

            <button
                type="button"
                :disabled="Boolean(pendingAction) || !canProcess"
                @click="$emit('action', 'escalate')"
                class="btn-escalate"
            >
                Escalate
            </button>
        </div>
    </section>
</template>

<style scoped>
.detail-panel {
    border: 1px solid #d8dee9;
    border-radius: 8px;
    background: #fff;
    min-height: 520px;
    padding: 24px;
}

.detail-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 22px;
}

h2 {
    margin-bottom: 0;
    font-size: 24px;
}

.eyebrow {
    margin-bottom: 6px;
    color: #526173;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.status-pill {
    border-radius: 999px;
    background: #e8eef7;
    padding: 6px 10px;
    color: #28364a;
    font-size: 13px;
    font-weight: 700;
}

.facts {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin: 0 0 22px;
}

.facts div {
    border: 1px solid #eef1f6;
    border-radius: 6px;
    padding: 12px;
}

dt {
    color: #66758a;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
}

dd {
    margin: 4px 0 0;
}

.summary {
    max-width: 720px;
    color: #2c384a;
    line-height: 1.55;
}

.notes {
    color: #66758a;
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 28px;
}

.actions button {
    border: 1px solid #bac5d5;
    border-radius: 6px;
    background: #fff;
    padding: 10px 14px;
    color: #1d2433;
    cursor: pointer;
}

.actions button:hover:not(:disabled) {
    border-color: #4c7bd9;
    color: #1e55bd;
}

.actions button:disabled {
    cursor: not-allowed;
    opacity: 0.6;
}
</style>
