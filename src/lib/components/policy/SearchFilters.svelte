<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let facets: any = {
		municipalities: [],
		categories: [],
		sources: []
	};
	export let filters: any = {
		municipalities: [],
		categories: [],
		document_type: '',
		date_from: '',
		date_to: ''
	};

	let selectedMunicipalities = filters.municipalities || [];
	let selectedCategories = filters.categories || [];
	let documentType = filters.document_type || '';
	let dateFrom = filters.date_from || '';
	let dateTo = filters.date_to || '';

	$: municipalityFacets = facets?.municipalities || [];
	$: categoryFacets = facets?.categories || [];

	function applyFilters() {
		dispatch('change', {
			query: '',
			filters: {
				municipalities: selectedMunicipalities,
				categories: selectedCategories,
				document_type: documentType,
				date_from: dateFrom,
				date_to: dateTo
			}
		});
	}

	function clearFilters() {
		selectedMunicipalities = [];
		selectedCategories = [];
		documentType = '';
		dateFrom = '';
		dateTo = '';
		applyFilters();
	}

	function toggleMunicipality(municipality: string) {
		if (selectedMunicipalities.includes(municipality)) {
			selectedMunicipalities = selectedMunicipalities.filter((m) => m !== municipality);
		} else {
			selectedMunicipalities = [...selectedMunicipalities, municipality];
		}
		applyFilters();
	}

	function toggleCategory(category: string) {
		if (selectedCategories.includes(category)) {
			selectedCategories = selectedCategories.filter((c) => c !== category);
		} else {
			selectedCategories = [...selectedCategories, category];
		}
		applyFilters();
	}
</script>

<div class="search-filters bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
			{$i18n.t('policy.filters.title')}
		</h3>
		<button
			on:click={clearFilters}
			class="text-xs text-blue-600 dark:text-blue-400 hover:underline"
		>
			{$i18n.t('policy.filters.clear_all')}
		</button>
	</div>

	<div class="space-y-4">
		<!-- Municipality Filter -->
		{#if municipalityFacets.length > 0}
			<div class="filter-section">
				<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					{$i18n.t('policy.filters.municipality')}
				</h4>
				<div class="space-y-2 max-h-48 overflow-y-auto">
					{#each municipalityFacets as facet}
						<label class="flex items-center cursor-pointer group">
							<input
								type="checkbox"
								checked={selectedMunicipalities.includes(facet.value)}
								on:change={() => toggleMunicipality(facet.value)}
								class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
							/>
							<span class="ml-2 text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-gray-100">
								{facet.value}
								<span class="text-xs text-gray-500">({facet.count})</span>
							</span>
						</label>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Category Filter -->
		{#if categoryFacets.length > 0}
			<div class="filter-section">
				<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
					{$i18n.t('policy.filters.category')}
				</h4>
				<div class="space-y-2 max-h-48 overflow-y-auto">
					{#each categoryFacets as facet}
						<label class="flex items-center cursor-pointer group">
							<input
								type="checkbox"
								checked={selectedCategories.includes(facet.value)}
								on:change={() => toggleCategory(facet.value)}
								class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
							/>
							<span class="ml-2 text-sm text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-gray-100">
								{facet.value}
								<span class="text-xs text-gray-500">({facet.count})</span>
							</span>
						</label>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Document Type Filter -->
		<div class="filter-section">
			<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
				{$i18n.t('policy.filters.document_type')}
			</h4>
			<select
				bind:value={documentType}
				on:change={applyFilters}
				class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md
					   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
					   focus:outline-none focus:ring-2 focus:ring-blue-500"
			>
				<option value="">{$i18n.t('policy.filters.all_types')}</option>
				<option value="pdf">PDF</option>
				<option value="html">HTML</option>
				<option value="docx">DOCX</option>
				<option value="xlsx">XLSX</option>
			</select>
		</div>

		<!-- Date Range Filter -->
		<div class="filter-section">
			<h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
				{$i18n.t('policy.filters.date_range')}
			</h4>
			<div class="space-y-2">
				<div>
					<label class="text-xs text-gray-600 dark:text-gray-400">
						{$i18n.t('policy.filters.date_from')}
					</label>
					<input
						type="date"
						bind:value={dateFrom}
						on:change={applyFilters}
						class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md
							   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
							   focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>
				<div>
					<label class="text-xs text-gray-600 dark:text-gray-400">
						{$i18n.t('policy.filters.date_to')}
					</label>
					<input
						type="date"
						bind:value={dateTo}
						on:change={applyFilters}
						class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md
							   bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100
							   focus:outline-none focus:ring-2 focus:ring-blue-500"
					/>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.filter-section {
		padding-bottom: 1rem;
		border-bottom: 1px solid rgba(229, 231, 235, 0.5);
	}

	.filter-section:last-child {
		border-bottom: none;
		padding-bottom: 0;
	}
</style>
