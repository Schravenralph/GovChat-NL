<script lang="ts">
	import { getContext, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { getSavedSearches, deleteSavedSearch } from '$lib/apis/policy';

	const i18n = getContext('i18n');

	let savedSearches: any[] = [];
	let loading = false;

	onMount(async () => {
		await loadSavedSearches();
	});

	async function loadSavedSearches() {
		try {
			loading = true;
			savedSearches = await getSavedSearches();
		} catch (error) {
			console.error('Failed to load saved searches:', error);
		} finally {
			loading = false;
		}
	}

	async function handleDelete(searchId: string) {
		if (!confirm($i18n.t('policy.saved_searches.confirm_delete'))) {
			return;
		}

		try {
			await deleteSavedSearch(searchId);
			savedSearches = savedSearches.filter((s) => s.id !== searchId);
			toast.success($i18n.t('policy.saved_searches.deleted'));
		} catch (error) {
			toast.error($i18n.t('policy.saved_searches.delete_error'));
		}
	}
</script>

{#if savedSearches.length > 0}
	<div class="saved-searches bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
		<h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
			{$i18n.t('policy.saved_searches.title')}
		</h3>

		<div class="space-y-2">
			{#each savedSearches as search (search.id)}
				<div class="flex items-center justify-between p-2 hover:bg-gray-50 dark:hover:bg-gray-750 rounded">
					<button
						class="flex-1 text-left text-sm text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
						on:click={() => {
							// Navigate to search with saved query
							window.location.href = `/policy?q=${encodeURIComponent(search.query_text)}`;
						}}
					>
						{search.name}
					</button>
					<button
						on:click={() => handleDelete(search.id)}
						class="text-gray-400 hover:text-red-600 dark:hover:text-red-400 ml-2"
						aria-label={$i18n.t('policy.saved_searches.delete')}
					>
						<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
							/>
						</svg>
					</button>
				</div>
			{/each}
		</div>
	</div>
{/if}
