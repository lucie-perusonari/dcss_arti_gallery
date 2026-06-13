# Admin Frontend Processing Layers

This document defines the API boundary and UI layers for the crawl operations dashboard.

## Project Boundary

- Module: `admin-frontend/`
- Role: bring the admin crawl-status and Gallery API metrics responses into React UI state and render the operations dashboard
- Input: `/admin/crawl-status`, `/admin/metrics/gallery-api` responses
- Output: browser UI state

## Internal Layers

- `src/api/status.ts`: admin API client backed by `VITE_ADMIN_API_URL`
- `src/types/status.ts`: admin status TypeScript types
- `src/App.tsx`: crawl status dashboard UI
- `src/styles.css`: dashboard layout and status styling

## Related Docs

- [Admin Frontend Data Types](./data-types.md)
- [Admin API Data Types](../../../admin_api/docs/en/data-types.md)
