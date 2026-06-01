import apiClient from './index';
import { toCamelCase } from './utils';

export type FetchSelectionResponse = {
  date: string;
  savedCount: number;
  message: string;
};

export const selectionApi = {
  async fetchSelection(date?: string): Promise<FetchSelectionResponse> {
    const params = date ? { date } : {};
    const response = await apiClient.post('/api/v1/select/fetch', null, { 
      params,
      timeout: 120000, // 2分钟超时，因为需要从东方财富获取大量数据
    });
    return toCamelCase(response.data);
  },
};
