import { WEBUI_API_BASE_URL } from '$lib/constants';

const BASE_URL = `${WEBUI_API_BASE_URL}/policy`;

function getToken(): string {
	if (typeof localStorage !== 'undefined') {
		return localStorage.getItem('token') || '';
	}
	return '';
}

async function handleResponse(response: Response) {
	if (!response.ok) {
		const error = await response.json().catch(() => ({
			detail: response.statusText
		}));
		throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
	}
	return response.json();
}

// Search API

export interface SearchRequest {
	query: string;
	filters?: {
		sources?: string[];
		municipalities?: string[];
		categories?: string[];
		date_from?: string;
		date_to?: string;
		document_type?: string;
	};
	page?: number;
	limit?: number;
	sort?: string;
}

export interface SearchResponse {
	results: any[];
	total: number;
	facets: {
		sources: Array<{ value: string; count: number }>;
		municipalities: Array<{ value: string; count: number }>;
		categories: Array<{ value: string; count: number }>;
	};
	page: number;
	took_ms: number;
}

export async function searchPolicyDocuments(request: SearchRequest): Promise<SearchResponse> {
	const response = await fetch(`${BASE_URL}/search`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${getToken()}`
		},
		body: JSON.stringify(request)
	});

	return handleResponse(response);
}

export async function getSearchFilters(): Promise<any> {
	const response = await fetch(`${BASE_URL}/search/filters`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

// Document API

export async function getPolicyDocument(documentId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/documents/${documentId}`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export async function getPolicyDocuments(params?: {
	source_id?: string;
	municipality?: string;
	status_filter?: string;
	limit?: number;
	offset?: number;
}): Promise<any[]> {
	const queryParams = new URLSearchParams();
	if (params?.source_id) queryParams.set('source_id', params.source_id);
	if (params?.municipality) queryParams.set('municipality', params.municipality);
	if (params?.status_filter) queryParams.set('status_filter', params.status_filter);
	if (params?.limit) queryParams.set('limit', params.limit.toString());
	if (params?.offset) queryParams.set('offset', params.offset.toString());

	const url = `${BASE_URL}/documents${queryParams.toString() ? `?${queryParams}` : ''}`;

	const response = await fetch(url, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export async function downloadPolicyDocument(
	documentId: string,
	format: string = 'original'
): Promise<void> {
	const response = await fetch(`${BASE_URL}/documents/${documentId}/download?format=${format}`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	if (!response.ok) {
		throw new Error(`Download failed: ${response.statusText}`);
	}

	// Handle file download
	const blob = await response.blob();
	const url = window.URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = `document_${documentId}.${format === 'pdf' ? 'pdf' : 'bin'}`;
	document.body.appendChild(a);
	a.click();
	document.body.removeChild(a);
	window.URL.revokeObjectURL(url);
}

// Favorites API

export async function getFavoriteDocuments(): Promise<any[]> {
	const response = await fetch(`${BASE_URL}/documents/favorites/list`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export async function addFavorite(documentId: string, notes?: string): Promise<any> {
	const url = notes
		? `${BASE_URL}/documents/${documentId}/favorite?notes=${encodeURIComponent(notes)}`
		: `${BASE_URL}/documents/${documentId}/favorite`;

	const response = await fetch(url, {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export async function removeFavorite(documentId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/documents/${documentId}/favorite`, {
		method: 'DELETE',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

// Saved Searches API

export interface SavedSearchRequest {
	name: string;
	query_text: string;
	filters?: Record<string, any>;
	notification_enabled?: boolean;
	notification_frequency?: 'immediate' | 'daily' | 'weekly';
}

export async function getSavedSearches(): Promise<any[]> {
	const response = await fetch(`${BASE_URL}/documents/saved-searches/list`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export async function createSavedSearch(request: SavedSearchRequest): Promise<any> {
	const response = await fetch(`${BASE_URL}/documents/saved-searches`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${getToken()}`
		},
		body: JSON.stringify(request)
	});

	return handleResponse(response);
}

export async function deleteSavedSearch(searchId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/documents/saved-searches/${searchId}`, {
		method: 'DELETE',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

// Admin: Policy Sources API

export async function getPolicySources(activeOnly: boolean = false): Promise<any[]> {
	const url = activeOnly ? `${BASE_URL}/sources?active_only=true` : `${BASE_URL}/sources`;

	const response = await fetch(url, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export async function getPolicySource(sourceId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/sources/${sourceId}`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export interface PolicySourceCreate {
	name: string;
	source_type: 'gemeenteblad' | 'dso' | 'custom';
	base_url: string;
	selector_config: Record<string, any>;
	auth_config?: Record<string, any>;
	rate_limit?: number;
	is_active?: boolean;
}

export async function createPolicySource(data: PolicySourceCreate): Promise<any> {
	const response = await fetch(`${BASE_URL}/sources`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${getToken()}`
		},
		body: JSON.stringify(data)
	});

	return handleResponse(response);
}

export async function updatePolicySource(sourceId: string, data: Partial<PolicySourceCreate>): Promise<any> {
	const response = await fetch(`${BASE_URL}/sources/${sourceId}/update`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${getToken()}`
		},
		body: JSON.stringify(data)
	});

	return handleResponse(response);
}

export async function deactivatePolicySource(sourceId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/sources/${sourceId}/deactivate`, {
		method: 'DELETE',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export async function deletePolicySource(sourceId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/sources/${sourceId}/delete`, {
		method: 'DELETE',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

// Admin: Scan Jobs API

export interface ScanJobRequest {
	job_type: 'full' | 'incremental' | 'manual';
	job_config?: Record<string, any>;
}

export async function triggerScan(sourceId: string, request: ScanJobRequest): Promise<any> {
	const response = await fetch(`${BASE_URL}/sources/${sourceId}/scan`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${getToken()}`
		},
		body: JSON.stringify(request)
	});

	return handleResponse(response);
}

export async function getScanJobs(sourceId: string, limit: number = 10): Promise<any[]> {
	const response = await fetch(`${BASE_URL}/sources/${sourceId}/scan/jobs?limit=${limit}`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}

export async function getScanJob(jobId: string): Promise<any> {
	const response = await fetch(`${BASE_URL}/sources/scan/jobs/${jobId}`, {
		method: 'GET',
		headers: {
			Authorization: `Bearer ${getToken()}`
		}
	});

	return handleResponse(response);
}
