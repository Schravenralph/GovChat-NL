import type { PageLoad } from './$types';

export const load: PageLoad = async ({ url }) => {
	// Extract search parameters from URL
	const query = url.searchParams.get('q') || '';
	const municipalities = url.searchParams.getAll('municipality');
	const categories = url.searchParams.getAll('category');
	const documentType = url.searchParams.get('document_type') || '';
	const dateFrom = url.searchParams.get('date_from') || '';
	const dateTo = url.searchParams.get('date_to') || '';
	const page = parseInt(url.searchParams.get('page') || '1', 10);
	const sort = url.searchParams.get('sort') || 'relevance';

	return {
		query,
		filters: {
			municipalities,
			categories,
			document_type: documentType,
			date_from: dateFrom,
			date_to: dateTo
		},
		page,
		sort
	};
};
