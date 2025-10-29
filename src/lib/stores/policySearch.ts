import { writable } from 'svelte/store';
import { searchPolicyDocuments } from '$lib/apis/policy';

export interface SearchFilters {
	sources?: string[];
	municipalities?: string[];
	categories?: string[];
	date_from?: string;
	date_to?: string;
	document_type?: string;
}

export interface SearchFacet {
	value: string;
	count: number;
}

export interface SearchFacets {
	sources: SearchFacet[];
	municipalities: SearchFacet[];
	categories: SearchFacet[];
}

export interface PolicyDocument {
	id: string;
	source_id: string;
	external_id?: string;
	title: string;
	description?: string;
	content_hash: string;
	document_url: string;
	document_type?: string;
	municipality?: string;
	publication_date?: Date | string | null;
	effective_date?: Date | string | null;
	file_size?: number;
	page_count?: number;
	language?: string;
	status: string;
	metadata?: Record<string, any>;
	created_at: number;
	updated_at: number;
	indexed_at?: number;
}

interface SearchState {
	query: string;
	filters: SearchFilters;
	results: PolicyDocument[];
	total: number;
	page: number;
	loading: boolean;
	error: string | null;
	facets: SearchFacets;
	took_ms: number;
}

const initialState: SearchState = {
	query: '',
	filters: {},
	results: [],
	total: 0,
	page: 1,
	loading: false,
	error: null,
	facets: {
		sources: [],
		municipalities: [],
		categories: []
	},
	took_ms: 0
};

function createPolicySearchStore() {
	const { subscribe, set, update } = writable<SearchState>(initialState);

	return {
		subscribe,

		async search(
			query: string,
			filters: SearchFilters = {},
			page: number = 1,
			sort: string = 'relevance'
		) {
			update((state) => ({
				...state,
				loading: true,
				error: null,
				query,
				filters,
				page
			}));

			try {
				const response = await searchPolicyDocuments({
					query,
					filters,
					page,
					limit: 20,
					sort
				});

				update((state) => ({
					...state,
					results: response.results,
					total: response.total,
					facets: response.facets,
					took_ms: response.took_ms,
					loading: false
				}));
			} catch (error: any) {
				update((state) => ({
					...state,
					loading: false,
					error: error.message || 'Search failed'
				}));
			}
		},

		reset() {
			set(initialState);
		},

		setFilters(filters: SearchFilters) {
			update((state) => ({
				...state,
				filters
			}));
		}
	};
}

export const policySearchStore = createPolicySearchStore();
