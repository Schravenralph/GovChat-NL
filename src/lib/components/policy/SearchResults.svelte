<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import DocumentCard from './DocumentCard.svelte';
	import Pagination from './Pagination.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let results: any[] = [];
	export let total: number = 0;
	export let currentPage: number = 1;
	export let limit: number = 20;
	export let sort: string = 'relevance';

	$: totalPages = Math.ceil(total / limit);
	$: startResult = (currentPage - 1) * limit + 1;
	$: endResult = Math.min(currentPage * limit, total);

	function handlePageChange(event: CustomEvent) {
		dispatch('pageChange', event.detail);
	}

	function handleSortChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		dispatch('sortChange', { sort: target.value });
	}
</script>

<div class="search-results">
	<div class="flex items-center justify-between mb-4">
		<div class="text-sm text-gray-600 dark:text-gray-400">
			{$i18n.t('policy.results.showing')} <span class="font-medium">{startResult}</span> -
			<span class="font-medium">{endResult}</span> {$i18n.t('policy.results.of')}
			<span class="font-medium">{total}</span> {$i18n.t('policy.results.results')}
		</div>

		<div class="flex items-center gap-2">
			<label for="sort-select" class="text-sm text-gray-600 dark:text-gray-400">
				{$i18n.t('policy.results.sort_by')}:
			</label>
			<select
				id="sort-select"
				bind:value={sort}
				on:change={handleSortChange}
				class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md
					   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
					   focus:outline-none focus:ring-2 focus:ring-blue-500"
			>
				<option value="relevance">{$i18n.t('policy.results.sort.relevance')}</option>
				<option value="date_desc">{$i18n.t('policy.results.sort.date_desc')}</option>
				<option value="date_asc">{$i18n.t('policy.results.sort.date_asc')}</option>
				<option value="title">{$i18n.t('policy.results.sort.title')}</option>
			</select>
		</div>
	</div>

	<div class="space-y-4">
		{#each results as document (document.id)}
			<DocumentCard {document} />
		{/each}
	</div>

	{#if totalPages > 1}
		<div class="mt-6">
			<Pagination
				{currentPage}
				{totalPages}
				on:pageChange={handlePageChange}
			/>
		</div>
	{/if}
</div>
