<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { policyDocumentsStore } from '$lib/stores/policyDocuments';

	const i18n = getContext('i18n');

	export let document: any;

	let isFavorite = false;
	let downloadingFormat: string | null = null;

	function formatDate(dateString: string | Date | null): string {
		if (!dateString) return '';
		const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
		return date.toLocaleDateString('nl-NL', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function formatFileSize(bytes: number | null): string {
		if (!bytes) return '';
		const mb = bytes / (1024 * 1024);
		return `${mb.toFixed(2)} MB`;
	}

	async function toggleFavorite() {
		try {
			if (isFavorite) {
				await policyDocumentsStore.removeFavorite(document.id);
				toast.success($i18n.t('policy.document.removed_from_favorites'));
			} else {
				await policyDocumentsStore.addFavorite(document.id);
				toast.success($i18n.t('policy.document.added_to_favorites'));
			}
			isFavorite = !isFavorite;
		} catch (error) {
			toast.error($i18n.t('policy.document.favorite_error'));
		}
	}

	async function handleDownload(format: string = 'original') {
		try {
			downloadingFormat = format;
			await policyDocumentsStore.downloadDocument(document.id, format);
			toast.success($i18n.t('policy.document.download_started'));
		} catch (error) {
			toast.error($i18n.t('policy.document.download_error'));
		} finally {
			downloadingFormat = null;
		}
	}

	function openExternalUrl() {
		if (document.document_url) {
			window.open(document.document_url, '_blank', 'noopener,noreferrer');
		}
	}
</script>

<div class="document-viewer">
	<div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
		<!-- Header -->
		<div class="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-gray-700 dark:to-gray-600 p-6">
			<h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
				{document.title}
			</h1>
			{#if document.description}
				<p class="text-gray-700 dark:text-gray-300">
					{document.description}
				</p>
			{/if}
		</div>

		<!-- Actions -->
		<div class="flex items-center gap-3 px-6 py-4 bg-gray-50 dark:bg-gray-750 border-b border-gray-200 dark:border-gray-700">
			<button
				on:click={() => handleDownload('original')}
				disabled={downloadingFormat !== null}
				class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md
					   hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
			>
				<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
				</svg>
				{#if downloadingFormat === 'original'}
					{$i18n.t('policy.document.downloading')}
				{:else}
					{$i18n.t('policy.document.download')}
				{/if}
			</button>

			<button
				on:click={toggleFavorite}
				class="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md
					   {isFavorite ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700' : 'bg-white dark:bg-gray-800'}
					   hover:bg-gray-50 dark:hover:bg-gray-700 transition"
			>
				<svg
					class="w-5 h-5 {isFavorite ? 'text-yellow-500 fill-current' : 'text-gray-500'}"
					fill={isFavorite ? 'currentColor' : 'none'}
					viewBox="0 0 24 24"
					stroke="currentColor"
				>
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
				</svg>
				{isFavorite ? $i18n.t('policy.document.favorited') : $i18n.t('policy.document.add_favorite')}
			</button>

			{#if document.document_url}
				<button
					on:click={openExternalUrl}
					class="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md
						   bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
				>
					<svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
					</svg>
					{$i18n.t('policy.document.view_original')}
				</button>
			{/if}
		</div>

		<!-- Metadata -->
		<div class="p-6">
			<h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
				{$i18n.t('policy.document.metadata')}
			</h2>

			<dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#if document.municipality}
					<div>
						<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$i18n.t('policy.document.fields.municipality')}
						</dt>
						<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">{document.municipality}</dd>
					</div>
				{/if}

				{#if document.publication_date}
					<div>
						<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$i18n.t('policy.document.fields.publication_date')}
						</dt>
						<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">
							{formatDate(document.publication_date)}
						</dd>
					</div>
				{/if}

				{#if document.effective_date}
					<div>
						<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$i18n.t('policy.document.fields.effective_date')}
						</dt>
						<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">
							{formatDate(document.effective_date)}
						</dd>
					</div>
				{/if}

				{#if document.document_type}
					<div>
						<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$i18n.t('policy.document.fields.document_type')}
						</dt>
						<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100 uppercase">
							{document.document_type}
						</dd>
					</div>
				{/if}

				{#if document.file_size}
					<div>
						<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$i18n.t('policy.document.fields.file_size')}
						</dt>
						<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">
							{formatFileSize(document.file_size)}
						</dd>
					</div>
				{/if}

				{#if document.page_count}
					<div>
						<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$i18n.t('policy.document.fields.page_count')}
						</dt>
						<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100">
							{document.page_count} {$i18n.t('policy.document.fields.pages')}
						</dd>
					</div>
				{/if}

				{#if document.language}
					<div>
						<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$i18n.t('policy.document.fields.language')}
						</dt>
						<dd class="mt-1 text-sm text-gray-900 dark:text-gray-100 uppercase">
							{document.language}
						</dd>
					</div>
				{/if}

				{#if document.status}
					<div>
						<dt class="text-sm font-medium text-gray-500 dark:text-gray-400">
							{$i18n.t('policy.document.fields.status')}
						</dt>
						<dd class="mt-1">
							<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
								{document.status === 'indexed' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}">
								{document.status}
							</span>
						</dd>
					</div>
				{/if}
			</dl>

			{#if document.metadata && Object.keys(document.metadata).length > 0}
				<div class="mt-6">
					<h3 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">
						{$i18n.t('policy.document.additional_metadata')}
					</h3>
					<div class="bg-gray-50 dark:bg-gray-750 rounded-lg p-4">
						<pre class="text-xs text-gray-700 dark:text-gray-300 overflow-auto">{JSON.stringify(
							document.metadata,
							null,
							2
						)}</pre>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>
