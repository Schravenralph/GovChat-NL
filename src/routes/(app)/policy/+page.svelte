<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import type { PageData } from './$types';

	import SearchBar from '$lib/components/policy/SearchBar.svelte';
	import SearchFilters from '$lib/components/policy/SearchFilters.svelte';
	import SearchResults from '$lib/components/policy/SearchResults.svelte';
	import SavedSearches from '$lib/components/policy/SavedSearches.svelte';
	import { policySearchStore } from '$lib/stores/policySearch';

	const i18n = getContext('i18n');

	export let data: PageData;

	let query = data.query;
	let filters = data.filters;
	let currentPage = data.page;
	let sort = data.sort;

	$: results = $policySearchStore.results;
	$: total = $policySearchStore.total;
	$: facets = $policySearchStore.facets;
	$: loading = $policySearchStore.loading;
	$: error = $policySearchStore.error;

	async function handleSearch(event: CustomEvent) {
		const { query: newQuery, filters: newFilters } = event.detail;
		query = newQuery;
		filters = newFilters || {};
		currentPage = 1;

		// Update URL
		updateURL();

		// Perform search
		await policySearchStore.search(query, filters, currentPage, sort);
	}

	async function handlePageChange(event: CustomEvent) {
		currentPage = event.detail.page;
		updateURL();
		await policySearchStore.search(query, filters, currentPage, sort);

		// Scroll to top
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	async function handleSortChange(event: CustomEvent) {
		sort = event.detail.sort;
		currentPage = 1;
		updateURL();
		await policySearchStore.search(query, filters, currentPage, sort);
	}

	function updateURL() {
		const params = new URLSearchParams();
		if (query) params.set('q', query);
		if (filters.municipalities?.length) {
			filters.municipalities.forEach((m: string) => params.append('municipality', m));
		}
		if (filters.categories?.length) {
			filters.categories.forEach((c: string) => params.append('category', c));
		}
		if (filters.document_type) params.set('document_type', filters.document_type);
		if (filters.date_from) params.set('date_from', filters.date_from);
		if (filters.date_to) params.set('date_to', filters.date_to);
		if (currentPage > 1) params.set('page', currentPage.toString());
		if (sort !== 'relevance') params.set('sort', sort);

		const url = params.toString() ? `?${params.toString()}` : '/policy';
		goto(url, { keepFocus: true, noScroll: true, replaceState: true });
	}

	onMount(() => {
		// If there's a query from URL, perform search
		if (query) {
			policySearchStore.search(query, filters, currentPage, sort);
		}
	});
</script>

<div class="policy-search-page h-full overflow-auto">
	<div class="max-w-7xl mx-auto px-4 py-6">
		<div class="mb-6">
			<h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">
				{$i18n.t('policy.search.title')}
			</h1>
			<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
				{$i18n.t('policy.search.subtitle')}
			</p>
		</div>

		<div class="mb-6">
			<SearchBar
				{query}
				{loading}
				on:search={handleSearch}
			/>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
			<!-- Filters Sidebar -->
			<aside class="lg:col-span-1">
				<div class="sticky top-6 space-y-4">
					<SearchFilters
						{facets}
						{filters}
						on:change={handleSearch}
					/>

					<SavedSearches />
				</div>
			</aside>

			<!-- Results Main Area -->
			<main class="lg:col-span-3">
				{#if error}
					<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
						<p class="text-red-800 dark:text-red-200">
							{$i18n.t('policy.search.error')}: {error}
						</p>
					</div>
				{:else if loading}
					<div class="flex items-center justify-center py-12">
						<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-gray-100"></div>
					</div>
				{:else if query && results.length === 0}
					<div class="text-center py-12">
						<svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
						</svg>
						<h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">
							{$i18n.t('policy.search.no_results')}
						</h3>
						<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
							{$i18n.t('policy.search.try_different_query')}
						</p>
					</div>
				{:else if results.length > 0}
					<SearchResults
						{results}
						{total}
						{currentPage}
						limit={20}
						{sort}
						on:pageChange={handlePageChange}
						on:sortChange={handleSortChange}
					/>
				{:else}
					<div class="text-center py-12">
						<svg class="mx-auto h-16 w-16 text-gray-300 dark:text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
						</svg>
						<h3 class="mt-4 text-lg font-medium text-gray-900 dark:text-gray-100">
							{$i18n.t('policy.search.empty_state_title')}
						</h3>
						<p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
							{$i18n.t('policy.search.empty_state_message')}
						</p>
					</div>
				{/if}
			</main>
		</div>
	</div>
</div>

<style>
	.policy-search-page {
		background-color: var(--background-color, white);
	}

	@media (max-width: 1024px) {
		.policy-search-page .grid {
			grid-template-columns: 1fr;
		}

		aside {
			position: relative;
		}
	}
</style>
