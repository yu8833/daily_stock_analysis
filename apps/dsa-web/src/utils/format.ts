import React from 'react';

export const formatDateTime = (value?: string | null): string => {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
};

export const formatDate = (value?: string): string => {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;

  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);
};

export const toDateInputValue = (date: Date): string => {
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export const getRecentStartDate = (days: number): string => {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai' }).format(date);
};

export const getTodayInShanghai = (): string =>
  new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Shanghai' }).format(new Date());

export const formatReportType = (value?: string): string => {
  if (!value) return '—';
  if (value === 'simple') return '普通';
  if (value === 'detailed') return '标准';
  return value;
};

export const formatPct = (value: number | null | undefined): string => {
  if (value == null) return '-';
  const formatted = value >= 0 ? `+${value.toFixed(2)}%` : `${value.toFixed(2)}%`;
  return formatted;
};

export const formatNumber = (value: number | null | undefined): string => {
  if (value == null) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toFixed(0);
};

export const formatMoney = (value: number | null | undefined): string => {
  if (value == null) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toFixed(2);
};

export const formatPrice = (value: number | null | undefined): string => {
  if (value == null) return '-';
  return value.toFixed(2);
};

export const formatVolume = (value: number | null | undefined): string => {
  if (value == null) return '-';
  if (Math.abs(value) >= 100000000) {
    return `${(value / 100000000).toFixed(2)}亿`;
  }
  if (Math.abs(value) >= 10000) {
    return `${(value / 10000).toFixed(2)}万`;
  }
  return value.toLocaleString();
};

export const getValueColor = (value: number | null | undefined, type: string): string => {
  if (type === 'percent' && value !== null && value !== undefined) {
    if (value > 0) return 'text-red-600 dark:text-red-400';
    if (value < 0) return 'text-green-600 dark:text-green-400';
  }
  if (type === 'money' && value !== null && value !== undefined) {
    if (value > 0) return 'text-red-600 dark:text-red-400';
    if (value < 0) return 'text-green-600 dark:text-green-400';
  }
  return '';
};

export const getEastMoneyUrl = (code: string): string => {
  if (code.startsWith('6') || code.startsWith('5') || code.startsWith('9')) {
    return `https://quote.eastmoney.com/sh${code}.html`;
  } else {
    return `https://quote.eastmoney.com/sz${code}.html`;
  }
};

export const getTodayIso = (): string => {
  const today = new Date();
  return today.toISOString().split('T')[0];
};

export type ValueType = 'text' | 'number' | 'percent' | 'money' | 'price' | 'date' | 'flag';

export interface ColumnConfig<T> {
  key: keyof T;
  label: string;
  width: string;
  align: 'left' | 'right' | 'center';
  type: ValueType;
  render?: (value: any, row: T) => React.ReactNode;
}

export const formatCellValue = <T,>(value: any, column: ColumnConfig<T>): string => {
  if (value === null || value === undefined) return '-';

  switch (column.type) {
    case 'price':
      return formatPrice(value);
    case 'percent':
      return formatPct(value);
    case 'money':
      return formatMoney(value);
    case 'number':
      return formatNumber(value);
    case 'date':
      return formatDate(value);
    default:
      return String(value);
  }
};
