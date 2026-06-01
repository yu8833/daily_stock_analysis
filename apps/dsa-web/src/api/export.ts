import apiClient from './index';

/**
 * 导出选股数据
 * @param format 导出格式: 'csv' 或 'excel'
 * @param date 日期 (可选)
 */
export async function exportSelection(
  format: 'csv' | 'excel' = 'csv',
  date?: string
): Promise<void> {
  const params = new URLSearchParams({ format });
  if (date) {
    params.append('date', date);
  }

  const response = await apiClient.get(`/api/v1/export/selection?${params.toString()}`, {
    responseType: 'blob',
  });

  downloadFile(response, format);
}

/**
 * 导出买入信号数据
 * @param format 导出格式: 'csv' 或 'excel'
 * @param date 日期 (可选)
 */
export async function exportBuySignals(
  format: 'csv' | 'excel' = 'csv',
  date?: string
): Promise<void> {
  const params = new URLSearchParams({ format });
  if (date) {
    params.append('date', date);
  }

  const response = await apiClient.get(`/api/v1/export/buy-signals?${params.toString()}`, {
    responseType: 'blob',
  });

  downloadFile(response, format);
}

/**
 * 导出卖出信号数据
 * @param format 导出格式: 'csv' 或 'excel'
 * @param date 日期 (可选)
 */
export async function exportSellSignals(
  format: 'csv' | 'excel' = 'csv',
  date?: string
): Promise<void> {
  const params = new URLSearchParams({ format });
  if (date) {
    params.append('date', date);
  }

  const response = await apiClient.get(`/api/v1/export/sell-signals?${params.toString()}`, {
    responseType: 'blob',
  });

  downloadFile(response, format);
}

/**
 * 下载文件
 * @param response Axios响应
 * @param format 文件格式
 */
function downloadFile(response: any, format: 'csv' | 'excel'): void {
  // 从响应头获取文件名，如果没有则生成默认文件名
  const contentDisposition = response.headers['content-disposition'];
  let filename = contentDisposition 
    ? contentDisposition.match(/filename="?([^"]+)"?/)?.[1]
    : null;

  if (!filename) {
    const now = new Date();
    const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, -5);
    filename = `export_${timestamp}.${format === 'excel' ? 'xlsx' : 'csv'}`;
  }

  // 创建下载链接
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
