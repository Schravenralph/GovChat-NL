<script lang="ts">
	import { createEventDispatcher } from 'svelte';

	const dispatch = createEventDispatcher();

	export let currentPage: number;
	export let totalPages: number;

	$: pages = getPageNumbers(currentPage, totalPages);

	function getPageNumbers(current: number, total: number): (number | string)[] {
		const delta = 2;
		const range: (number | string)[] = [];
		const rangeWithDots: (number | string)[] = [];

		for (
			let i = Math.max(2, current - delta);
			i <= Math.min(total - 1, current + delta);
			i++
		) {
			range.push(i);
		}

		if (current - delta > 2) {
			range.unshift('...');
		}
		if (current + delta < total - 1) {
			range.push('...');
		}

		range.unshift(1);
		if (total > 1) {
			range.push(total);
		}

		return range;
	}

	function goToPage(page: number) {
		if (page >= 1 && page <= totalPages && page !== currentPage) {
			dispatch('pageChange', { page });
		}
	}

	function previousPage() {
		if (currentPage > 1) {
			goToPage(currentPage - 1);
		}
	}

	function nextPage() {
		if (currentPage < totalPages) {
			goToPage(currentPage + 1);
		}
	}
</script>

<nav class="flex items-center justify-center" aria-label="Pagination">
	<div class="flex items-center gap-1">
		<button
			on:click={previousPage}
			disabled={currentPage === 1}
			class="px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600
				   bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300
				   hover:bg-gray-50 dark:hover:bg-gray-700
				   disabled:opacity-50 disabled:cursor-not-allowed
				   transition"
			aria-label="Previous page"
		>
			<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
		</button>

		{#each pages as page}
			{#if page === '...'}
				<span class="px-3 py-2 text-gray-500">...</span>
			{:else}
				<button
					on:click={() => goToPage(page)}
					class="px-4 py-2 rounded-md border transition
						   {page === currentPage
						? 'border-blue-500 bg-blue-500 text-white'
						: 'border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'}"
					aria-label="Page {page}"
					aria-current={page === currentPage ? 'page' : undefined}
				>
					{page}
				</button>
			{/if}
		{/each}

		<button
			on:click={nextPage}
			disabled={currentPage === totalPages}
			class="px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600
				   bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300
				   hover:bg-gray-50 dark:hover:bg-gray-700
				   disabled:opacity-50 disabled:cursor-not-allowed
				   transition"
			aria-label="Next page"
		>
			<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
			</svg>
		</button>
	</div>
</nav>
