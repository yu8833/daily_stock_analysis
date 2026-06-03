import apiClient from './index';

export type ChipRaceItem = {
  code: string;
  name: string;
  date: string;
  period: number;
  latest_price?: number | null;
  change_pct?: number | null;
  prev_close?: number | null;
  open_price?: number | null;
  amount?: number | null;
  race_amount?: number | null;
  race_ratio?: number | null;
  race_pct?: number | null;
  board_days?: number | null;
  board_type?: string | null;
};

export const marketDataApi = {
  async getRaceOpen(queryDate?: string): Promise<ChipRaceItem[]> {
    const params: Record<string, string> = {};
    if (queryDate) {
      params.query_date = queryDate;
    }
    const response = await apiClient.get('/api/v1/market/zpqc', { params });
    return response.data as ChipRaceItem[];
  },

  async getRaceClose(queryDate?: string): Promise<ChipRaceItem[]> {
    const params: Record<string, string> = {};
    if (queryDate) {
      params.query_date = queryDate;
    }
    const response = await apiClient.get('/api/v1/market/wpqc', { params });
    return response.data as ChipRaceItem[];
  },
};