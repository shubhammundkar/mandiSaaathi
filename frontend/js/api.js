// Mandi Saathi - Centralized API Client with Timeout, Error Handling, and Loading State

const DEFAULT_TIMEOUT_MS = 12000;

class ApiClient {
  constructor() {
    this.activeRequests = 0;
    this.loadingListeners = [];
  }

  onLoading(listener) {
    if (typeof listener === 'function') {
      this.loadingListeners.push(listener);
    }
  }

  _notifyLoading() {
    const isLoading = this.activeRequests > 0;
    this.loadingListeners.forEach((fn) => fn(isLoading));
  }

  async fetchWithTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    this.activeRequests += 1;
    this._notifyLoading();

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        }
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        let errMessage = `Server error (${response.status})`;
        try {
          const errData = await response.json();
          if (errData && errData.detail) {
            errMessage = typeof errData.detail === 'string' ? errData.detail : JSON.stringify(errData.detail);
          }
        } catch (_) {
          // Response body was not JSON
        }
        const error = new Error(errMessage);
        error.status = response.status;
        throw error;
      }

      return await response.json();
    } catch (err) {
      if (err.name === 'AbortError') {
        const timeoutError = new Error(`Request timed out after ${timeoutMs / 1000} seconds. Please check your connection.`);
        timeoutError.isTimeout = true;
        throw timeoutError;
      }
      throw err;
    } finally {
      clearTimeout(timeoutId);
      this.activeRequests = Math.max(0, this.activeRequests - 1);
      this._notifyLoading();
    }
  }

  // --- API Endpoints ---

  async getDataStatus() {
    return this.fetchWithTimeout('/api/data-status');
  }

  async getCrops() {
    return this.fetchWithTimeout('/api/crops');
  }

  async getMandis(crop = '') {
    const query = crop ? `?crop=${encodeURIComponent(crop)}` : '';
    return this.fetchWithTimeout(`/api/mandis${query}`);
  }

  async calculateAdvise(payload) {
    return this.fetchWithTimeout('/api/advise', {
      method: 'POST',
      body: JSON.stringify(payload)
    }, 15000);
  }

  async getForecast(crop, market) {
    return this.fetchWithTimeout(`/api/forecast?crop=${encodeURIComponent(crop)}&market=${encodeURIComponent(market)}`);
  }

  async getStorageAdvice(crop, market = '') {
    const mktParam = market ? `&market=${encodeURIComponent(market)}` : '';
    return this.fetchWithTimeout(`/api/storage-advice?crop=${encodeURIComponent(crop)}${mktParam}`);
  }

  async getBacktest(crop, district = '', quantity = 20.0, vehicle = 'tempo') {
    const params = new URLSearchParams({ crop });
    if (district) params.append('district', district);
    if (quantity) params.append('quantity', quantity);
    if (vehicle) params.append('vehicle', vehicle);
    return this.fetchWithTimeout(`/api/backtest?${params.toString()}`, {}, 18000);
  }

  async sendChat(message, language = null, sessionId = null) {
    return this.fetchWithTimeout('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        language: language || undefined,
        session_id: sessionId || undefined
      })
    }, 15000);
  }
}

export const api = new ApiClient();
export default api;
