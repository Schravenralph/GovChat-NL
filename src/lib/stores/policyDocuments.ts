import { writable } from 'svelte/store';
import {
	getPolicyDocument,
	downloadPolicyDocument,
	addFavorite,
	removeFavorite
} from '$lib/apis/policy';
import type { PolicyDocument } from './policySearch';

interface DocumentsState {
	documents: Record<string, PolicyDocument>;
	favorites: string[];
	loading: boolean;
	error: string | null;
}

const initialState: DocumentsState = {
	documents: {},
	favorites: [],
	loading: false,
	error: null
};

function createPolicyDocumentsStore() {
	const { subscribe, set, update } = writable<DocumentsState>(initialState);

	return {
		subscribe,

		async loadDocument(documentId: string) {
			update((state) => ({
				...state,
				loading: true,
				error: null
			}));

			try {
				const document = await getPolicyDocument(documentId);

				update((state) => ({
					...state,
					documents: {
						...state.documents,
						[documentId]: document
					},
					loading: false
				}));

				return document;
			} catch (error: any) {
				update((state) => ({
					...state,
					loading: false,
					error: error.message || 'Failed to load document'
				}));
				throw error;
			}
		},

		async downloadDocument(documentId: string, format: string = 'original') {
			try {
				await downloadPolicyDocument(documentId, format);
			} catch (error: any) {
				throw error;
			}
		},

		async addFavorite(documentId: string, notes?: string) {
			try {
				await addFavorite(documentId, notes);

				update((state) => ({
					...state,
					favorites: [...state.favorites, documentId]
				}));
			} catch (error: any) {
				throw error;
			}
		},

		async removeFavorite(documentId: string) {
			try {
				await removeFavorite(documentId);

				update((state) => ({
					...state,
					favorites: state.favorites.filter((id) => id !== documentId)
				}));
			} catch (error: any) {
				throw error;
			}
		},

		cacheDocument(document: PolicyDocument) {
			update((state) => ({
				...state,
				documents: {
					...state.documents,
					[document.id]: document
				}
			}));
		},

		clearCache() {
			set(initialState);
		}
	};
}

export const policyDocumentsStore = createPolicyDocumentsStore();
