<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let query = '';
	export let loading = false;

	let inputElement: HTMLInputElement;
	let showClearButton = query.length > 0;

	$: showClearButton = query.length > 0;

	function handleSubmit() {
		if (query.trim().length > 0) {
			dispatch('search', { query: query.trim() });
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter') {
			event.preventDefault();
			handleSubmit();
		}
	}

	function clearSearch() {
		query = '';
		inputElement?.focus();
	}
</script>

<div class="search-bar">
	<div class="relative">
		<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
			<svg
				class="h-5 w-5 text-gray-400"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
				/>
			</svg>
		</div>

		<input
			bind:this={inputElement}
			bind:value={query}
			on:keydown={handleKeydown}
			type="text"
			disabled={loading}
			placeholder={$i18n.t('policy.search.placeholder')}
			class="w-full pl-10 pr-24 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
				   bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100
				   placeholder-gray-500 dark:placeholder-gray-400
				   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
				   disabled:opacity-50 disabled:cursor-not-allowed
				   transition"
		/>

		<div class="absolute inset-y-0 right-0 flex items-center pr-3 gap-2">
			{#if showClearButton && !loading}
				<button
					on:click={clearSearch}
					type="button"
					class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition"
					aria-label={$i18n.t('policy.search.clear')}
				>
					<svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M6 18L18 6M6 6l12 12"
						/>
					</svg>
				</button>
			{/if}

			<button
				on:click={handleSubmit}
				type="button"
				disabled={loading || query.trim().length === 0}
				class="px-4 py-1.5 bg-blue-600 text-white rounded-md
					   hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
					   transition text-sm font-medium"
			>
				{#if loading}
					<svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
						<circle
							class="opacity-25"
							cx="12"
							cy="12"
							r="10"
							stroke="currentColor"
							stroke-width="4"
						></circle>
						<path
							class="opacity-75"
							fill="currentColor"
							d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
						></path>
					</svg>
				{:else}
					{$i18n.t('policy.search.search_button')}
				{/if}
			</button>
		</div>
	</div>

	<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">
		{$i18n.t('policy.search.search_hint')}
	</p>
</div>

<style>
	.search-bar {
		width: 100%;
	}
</style>
