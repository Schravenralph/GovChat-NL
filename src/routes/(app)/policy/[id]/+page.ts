import type { PageLoad } from './$types';
import { getPolicyDocument } from '$lib/apis/policy';

export const load: PageLoad = async ({ params }) => {
	const documentId = params.id;

	return {
		documentId
	};
};
