import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api } from '../api';

describe('api object', () => {
  it('exposes all expected methods', () => {
    const expectedMethods = [
      'health',
      'listDocuments',
      'getDocument',
      'createDocument',
      'updateDocument',
      'deleteDocument',
      'searchDocuments',
      'classify',
      'migrate',
      'zoneSummary',
      'validate',
      'listSessions',
      'createSession',
      'getSession',
      'startWork',
      'endWork',
      'recordLoad',
      'wrapUp',
      'closeSession',
    ];

    expectedMethods.forEach((method) => {
      expect(api).toHaveProperty(method);
      expect(typeof api[method]).toBe('function');
    });
  });
});

describe('request error handling', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('throws an error when the response is not ok', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({ detail: 'Something went wrong' }),
      })
    );

    await expect(api.health()).rejects.toThrow('Something went wrong');
  });

  it('uses statusText as fallback when json parsing fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        statusText: 'Bad Gateway',
        json: () => Promise.reject(new Error('parse error')),
      })
    );

    await expect(api.health()).rejects.toThrow('Bad Gateway');
  });

  it('returns parsed json on success', async () => {
    const mockData = { status: 'ok' };
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockData),
      })
    );

    const result = await api.health();
    expect(result).toEqual(mockData);
  });
});
