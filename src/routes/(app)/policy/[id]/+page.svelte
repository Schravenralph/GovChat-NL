<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	import DocumentViewer from '$lib/components/policy/DocumentViewer.svelte';
	import { policyDocumentsStore } from '$lib/stores/policyDocuments';

	const i18n = getContext('i18n');

	export let data: PageData;

	let documentId = data.documentId;

	$: document = $policyDocumentsStore.documents[documentId];
	$: loading = $policyDocumentsStore.loading;
	$: error = $policyDocumentsStore.error;

	onMount(async () => {
		// Load document if not in cache
		if (!document) {
			await policyDocumentsStore.loadDocument(documentId);
		}
	});

	function handleBack() {
		goto('/policy');
	}
</script>

<div class="document-page h-full overflow-auto">
	<div class="max-w-5xl mx-auto px-4 py-6">
		<button
			on:click={handleBack}
			class="mb-4 flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition"
		>
			<svg class="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
			{$i18n.t('policy.document.back_to_search')}
		</button>

		{#if error}
			<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
				<h3 class="text-lg font-medium text-red-800 dark:text-red-200 mb-2">
					{$i18n.t('policy.document.error_title')}
				</h3>
				<p class="text-red-700 dark:text-red-300">{error}</p>
			</div>
		{:else if loading}
			<div class="flex items-center justify-center py-12">
				<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-100"></div>
			</div>
		{:else if document}
			<DocumentViewer {document} />
		{:else}
			<div class="text-center py-12">
				<p class="text-gray-600 dark:text-gray-400">
					{$i18n.t('policy.document.not_found')}
				</p>
			</div>
		{/if}
	</div>
</div>

<style>
	.document-page {
		background-color: var(--background-color, white);
	}
</style>
