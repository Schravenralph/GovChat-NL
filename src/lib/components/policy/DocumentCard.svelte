<script lang="ts">
	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';

	const i18n = getContext('i18n');

	export let document: any;

	function formatDate(dateString: string | Date | null): string {
		if (!dateString) return '';
		const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
		return date.toLocaleDateString('nl-NL', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function getDocumentTypeIcon(type: string): string {
		switch (type?.toLowerCase()) {
			case 'pdf':
				return 'M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z';
			case 'html':
				return 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4';
			case 'docx':
				return 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z';
			default:
				return 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z';
		}
	}

	function getDocumentTypeColor(type: string): string {
		switch (type?.toLowerCase()) {
			case 'pdf':
				return 'text-red-500';
			case 'html':
				return 'text-blue-500';
			case 'docx':
				return 'text-blue-600';
			case 'xlsx':
				return 'text-green-600';
			default:
				return 'text-gray-500';
		}
	}

	function handleClick() {
		goto(`/policy/${document.id}`);
	}
</script>

<div
	class="document-card bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700
		   hover:shadow-lg hover:border-gray-300 dark:hover:border-gray-600
		   transition-all duration-200 cursor-pointer"
	on:click={handleClick}
	on:keydown={(e) => e.key === 'Enter' && handleClick()}
	role="button"
	tabindex="0"
>
	<div class="p-4">
		<div class="flex items-start gap-3">
			<div class="flex-shrink-0 mt-1">
				<svg
					class="w-6 h-6 {getDocumentTypeColor(document.document_type)}"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d={getDocumentTypeIcon(document.document_type)}
					/>
				</svg>
			</div>

			<div class="flex-1 min-w-0">
				<h3 class="text-base font-semibold text-gray-900 dark:text-gray-100 mb-1 line-clamp-2">
					{document.title}
				</h3>

				{#if document.description}
					<p class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
						{document.description}
					</p>
				{/if}

				<div class="flex flex-wrap items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
					{#if document.municipality}
						<span class="flex items-center gap-1">
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
								/>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
								/>
							</svg>
							{document.municipality}
						</span>
					{/if}

					{#if document.publication_date}
						<span class="flex items-center gap-1">
							<svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
								/>
							</svg>
							{formatDate(document.publication_date)}
						</span>
					{/if}

					{#if document.document_type}
						<span class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs uppercase font-medium">
							{document.document_type}
						</span>
					{/if}
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.document-card:focus {
		outline: 2px solid rgb(59, 130, 246);
		outline-offset: 2px;
	}

	.line-clamp-2 {
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		overflow: hidden;
	}
</style>
