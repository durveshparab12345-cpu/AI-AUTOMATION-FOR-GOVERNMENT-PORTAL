import { usePagination } from '../../hooks/usePagination';

interface Column<T> {
  key: keyof T;
  label: string;
  render?: (value: unknown, row: T, idx: number) => React.ReactNode;
  width?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  total?: number;
  currentPage?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  loading?: boolean;
  rowsPerPageOptions?: number[];
  onRowClick?: (row: T) => void;
  keyExtractor?: (row: T, idx: number) => string;
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  total,
  currentPage = 1,
  pageSize = 10,
  onPageChange,
  onPageSizeChange,
  loading = false,
  rowsPerPageOptions = [5, 10, 25, 50],
  onRowClick,
  keyExtractor,
}: DataTableProps<T>) {
  const pagination = usePagination({ initialPage: currentPage, initialPageSize: pageSize });

  const getRowKey = (row: T, idx: number) => {
    return keyExtractor ? keyExtractor(row, idx) : String(idx);
  };

  const totalPages = total ? Math.ceil(total / (pageSize || 10)) : 1;
  const displayPage = currentPage || pagination.page;

  return (
    <div style={{ width: '100%', overflowX: 'auto' }}>
      {/* Table */}
      <table
        style={{
          width: '100%',
          borderCollapse: 'collapse',
          background: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '8px',
          overflow: 'hidden',
        }}
      >
        <thead>
          <tr style={{ borderBottom: '1px solid #334155', background: '#0f172a' }}>
            {columns.map((col) => (
              <th
                key={String(col.key)}
                style={{
                  padding: '0.75rem 1rem',
                  textAlign: 'left',
                  color: '#94a3b8',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  letterSpacing: '0.05em',
                  width: col.width,
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr>
              <td colSpan={columns.length} style={{ padding: '2rem', textAlign: 'center' }}>
                <span style={{ color: '#64748b' }}>Loading…</span>
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} style={{ padding: '2rem', textAlign: 'center' }}>
                <span style={{ color: '#64748b' }}>No data available</span>
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr
                key={getRowKey(row, idx)}
                onClick={() => onRowClick?.(row)}
                style={{
                  borderBottom: '1px solid #334155',
                  cursor: onRowClick ? 'pointer' : 'default',
                  background: idx % 2 === 0 ? '#1e293b' : '#0f172a',
                  transition: 'background-color 0.2s',
                }}
                onMouseEnter={(e) => {
                  if (onRowClick) {
                    (e.currentTarget as HTMLTableRowElement).style.backgroundColor = '#1e3a5f';
                  }
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLTableRowElement).style.backgroundColor =
                    idx % 2 === 0 ? '#1e293b' : '#0f172a';
                }}
              >
                {columns.map((col) => (
                  <td
                    key={String(col.key)}
                    style={{
                      padding: '0.75rem 1rem',
                      color: '#cbd5e1',
                      fontSize: '0.9rem',
                      width: col.width,
                    }}
                  >
                    {col.render ? col.render(row[col.key], row, idx) : String(row[col.key])}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>

      {/* Pagination controls */}
      {total && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '1rem',
            background: '#1e293b',
            border: '1px solid #334155',
            borderTop: 'none',
            borderBottomLeftRadius: '8px',
            borderBottomRightRadius: '8px',
            gap: '1rem',
          }}
        >
          <div style={{ color: '#64748b', fontSize: '0.85rem' }}>
            Showing {(displayPage - 1) * (pageSize || 10) + 1} to{' '}
            {Math.min(displayPage * (pageSize || 10), total)} of {total}
          </div>

          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange?.(Number(e.target.value))}
            style={{
              background: '#0f172a',
              color: '#cbd5e1',
              border: '1px solid #334155',
              borderRadius: '4px',
              padding: '0.4rem 0.6rem',
              fontSize: '0.85rem',
              cursor: 'pointer',
            }}
          >
            {rowsPerPageOptions.map((opt) => (
              <option key={opt} value={opt}>
                {opt} per page
              </option>
            ))}
          </select>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => onPageChange?.(displayPage - 1)}
              disabled={displayPage <= 1}
              style={{
                background: displayPage <= 1 ? '#334155' : '#1e293b',
                color: displayPage <= 1 ? '#64748b' : '#94a3b8',
                border: '1px solid #334155',
                borderRadius: '4px',
                padding: '0.4rem 0.75rem',
                cursor: displayPage <= 1 ? 'not-allowed' : 'pointer',
                fontSize: '0.85rem',
              }}
            >
              ← Prev
            </button>

            <div style={{ color: '#64748b', padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}>
              Page {displayPage} of {totalPages}
            </div>

            <button
              onClick={() => onPageChange?.(displayPage + 1)}
              disabled={displayPage >= totalPages}
              style={{
                background: displayPage >= totalPages ? '#334155' : '#1e293b',
                color: displayPage >= totalPages ? '#64748b' : '#94a3b8',
                border: '1px solid #334155',
                borderRadius: '4px',
                padding: '0.4rem 0.75rem',
                cursor: displayPage >= totalPages ? 'not-allowed' : 'pointer',
                fontSize: '0.85rem',
              }}
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
