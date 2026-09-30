# AI Portal Automation Frontend - Complete Guide

## 📋 Overview

This is a professional React 18 + TypeScript frontend for the AI Portal Automation Platform. It provides a complete dashboard-based interface for managing portals, workflows, cases, and automations.

## 🏗️ Architecture

### Directory Structure

```
src/
├── layouts/
│   ├── MainLayout.tsx         # Primary layout with header, sidebar, footer
│   └── AuthLayout.tsx         # Simple layout for authentication
├── pages/
│   ├── DashboardPage.tsx      # Main dashboard with metrics & activity
│   ├── PortalsPage.tsx        # Portal management interface
│   ├── WorkflowsPage.tsx      # Workflow creation & management
│   ├── CasesPage.tsx          # Case tracking & management
│   ├── AutomationsPage.tsx    # Automation tracking & monitoring
│   ├── SettingsPage.tsx       # Organization settings & user management
│   ├── UserProfilePage.tsx    # User profile & preferences
│   ├── PMJayDemoPage.tsx      # Demo/prototype execution
│   └── NotFoundPage.tsx       # 404 page
├── components/
│   ├── layout/
│   │   ├── Header.tsx         # Top navigation bar
│   │   ├── Sidebar.tsx        # Left sidebar navigation
│   │   └── Footer.tsx         # Footer
│   ├── common/
│   │   ├── Button.tsx         # Reusable button component
│   │   ├── Badge.tsx          # Status badges
│   │   ├── Card.tsx           # Card container
│   │   ├── Modal.tsx          # Modal dialog
│   │   ├── DataTable.tsx      # Reusable data table with pagination
│   │   ├── Loading.tsx        # Loading spinner
│   │   ├── Toast.tsx          # Toast notifications
│   │   └── ErrorBoundary.tsx  # Error boundary wrapper
│   └── forms/
│       ├── TextField.tsx      # Text input field
│       ├── SelectField.tsx    # Dropdown/select field
│       ├── TextAreaField.tsx  # Multi-line text field
│       └── FormSection.tsx    # Form section grouping
├── context/
│   └── AuthContext.tsx        # Authentication context & provider
├── hooks/
│   ├── useAuth.ts            # Hook for auth context
│   ├── useApi.ts             # Hook for API calls
│   ├── useForm.ts            # Hook for form handling
│   ├── usePagination.ts      # Hook for pagination
│   └── usePolling.ts         # Hook for polling operations
├── services/
│   └── api.ts                # Centralized API client
├── types/
│   └── index.ts              # Shared TypeScript types
├── App.tsx                   # Main app component with routing
└── main.tsx                  # Application entry point
```

## 🎯 Key Features

### 1. **Dashboard Page**
- Welcome greeting with user information
- Key metrics cards (Total Cases, Active Workflows, etc.)
- Quick action buttons
- Recent activity feed
- System status indicators

### 2. **Portal Management**
- List all portals with status indicators
- Create new portal with modal form
- Edit portal details inline
- Delete portal with confirmation
- Search and filter by status
- Pagination support

### 3. **Workflow Management**
- Create and manage workflows
- Version control and status tracking
- Workflow steps visualization
- Publish/unpublish workflows
- Search and filter capabilities

### 4. **Case Management**
- Create and track cases
- Beneficiary information display
- Case status workflow
- Search by case number or beneficiary
- Status filtering
- Estimated amount tracking

### 5. **Automation Tracking**
- Real-time automation progress visualization
- Step-by-step status tracking
- Progress bars with percentage
- Retry failed automations
- Summary statistics

### 6. **Organization Settings**
- Organization details view
- User management interface
- Role-based access control (RBAC)
- Audit log viewer
- Permission matrix

### 7. **User Profile**
- User information display
- Password change form
- Notification preferences
- Activity log
- Sign out functionality

## 🔧 Components

### Layout Components

#### MainLayout
```tsx
<MainLayout
  title="AI Portal Automation"
  navItems={navItems}
  activeHref={currentPage}
  onNavigate={(href) => setCurrentPage(href)}
>
  {/* Content */}
</MainLayout>
```

### Common Components

#### Button
```tsx
<Button
  variant="primary" | "secondary" | "danger" | "ghost"
  size="sm" | "md" | "lg"
  isLoading={boolean}
  onClick={() => {}}
>
  Click me
</Button>
```

#### Badge
```tsx
<Badge status="COMPLETED" | "FAILED" | "RUNNING" label="Custom Label" />
```

#### Card
```tsx
<Card
  title="Card Title"
  subtitle="Subtitle"
  footer="Footer content"
  hoverable={true}
  clickable={true}
>
  Content
</Card>
```

#### Modal
```tsx
<Modal
  isOpen={true}
  title="Modal Title"
  onClose={() => {}}
  onConfirm={() => {}}
  confirmLabel="Save"
  confirmLoading={false}
  size="md"
>
  Form content
</Modal>
```

#### DataTable
```tsx
<DataTable
  columns={columns}
  data={data}
  total={total}
  currentPage={page}
  pageSize={pageSize}
  onPageChange={(page) => {}}
  onPageSizeChange={(size) => {}}
  onRowClick={(row) => {}}
  loading={false}
/>
```

### Form Components

#### TextField
```tsx
<TextField
  label="Field Label"
  name="fieldName"
  value={value}
  onChange={handleChange}
  error={error}
  helperText="Helper text"
  fullWidth={true}
  required={true}
/>
```

#### SelectField
```tsx
<SelectField
  label="Select"
  name="select"
  options={[
    { value: '1', label: 'Option 1' },
    { value: '2', label: 'Option 2' },
  ]}
  value={value}
  onChange={handleChange}
  error={error}
  placeholder="Choose..."
/>
```

#### FormSection
```tsx
<FormSection
  title="Section Title"
  description="Optional description"
  columns={2}
>
  {/* Form fields */}
</FormSection>
```

## 🎨 Styling

### Color Scheme (Dark Theme)
- **Primary**: #3b82f6 (Blue)
- **Background**: #0f172a (Dark Blue)
- **Surface**: #1e293b (Slate)
- **Border**: #334155 (Slate)
- **Text**: #f1f5f9 (Light)
- **Muted**: #64748b (Gray)
- **Success**: #10b981 (Green)
- **Error**: #ef4444 (Red)
- **Warning**: #fbbf24 (Amber)

### Responsive Breakpoints
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

## 🔐 Authentication & Context

### AuthContext Usage
```tsx
import { useAuth } from './context/AuthContext';

function MyComponent() {
  const { auth, setAuth, logout, isAuthenticated } = useAuth();
  
  return (
    <div>
      {auth.email}
      <button onClick={logout}>Sign out</button>
    </div>
  );
}
```

## 🪝 Custom Hooks

### useForm
Form state management with validation:
```tsx
const { values, errors, touched, loading, handleChange, handleSubmit, reset } = useForm({
  initialValues: { name: '' },
  validate: (values) => {
    // Return array of FormError
  },
  onSubmit: async (values) => {
    // Handle submission
  },
});
```

### useApi
API request handling:
```tsx
const { data, loading, error, request } = useApi();
const result = await request('/endpoint', { method: 'POST', body: JSON.stringify({}) });
```

### usePagination
Pagination state:
```tsx
const { page, pageSize, goToPage, nextPage, prevPage, setPageSize } = usePagination();
```

### usePolling
Polling data:
```tsx
const poll = async () => {
  // Fetch latest data
};
usePolling(poll, 2000, enabled); // 2 second interval
```

## 📡 API Integration

### Service Module
All API calls are centralized in `src/services/api.ts`:

```tsx
import {
  login,
  listPortals,
  createCase,
  listWorkflows,
  // ... more functions
} from './services/api';
```

### Authentication
```tsx
const { access_token } = await login(email, password);
setToken(access_token); // Store in memory
```

### API Errors
```tsx
try {
  const data = await listPortals();
} catch (err) {
  if (err instanceof ApiError) {
    console.log(err.status, err.message);
  }
}
```

## 🚀 Getting Started

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```

### Build
```bash
npm run build
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

## 📝 Types Reference

See `src/types/index.ts` for complete type definitions:
- `Portal`, `Workflow`, `Case`, `User`, `Organization`
- `ExecutionStatus`, `CaseStatus`, `WorkflowStatus`, `PortalStatus`
- `PaginatedResponse`, `ApiResponse`
- All entity types with relationships

## ♿ Accessibility

All components include:
- ARIA labels
- Semantic HTML
- Keyboard navigation
- Focus management
- Color contrast compliance
- Screen reader support

## 🧪 Error Handling

### Error Boundary
```tsx
<ErrorBoundary fallback={(error, retry) => <div>{error.message}</div>}>
  {/* Your component */}
</ErrorBoundary>
```

### User Feedback
- Toast notifications for actions
- Error messages in forms
- Loading states on buttons
- Empty states in tables

## 📊 Performance

- Lazy component loading (potential with React.lazy)
- Optimized re-renders with useCallback
- Efficient state management with Context
- Pagination for large datasets
- Debounced search/filter

## 🔒 Security

- Token stored in memory only (not localStorage)
- Authorization header on all requests
- CSRF protection ready
- Input validation on forms
- XSS prevention with React escaping

## 📚 Component Usage Examples

### Creating a Portal
```tsx
const [isModalOpen, setIsModalOpen] = useState(false);
const { values, handleChange, handleSubmit } = useForm({
  initialValues: { name: '', description: '', url: '' },
  onSubmit: async (values) => {
    await createPortal(values);
  },
});

return (
  <>
    <Button onClick={() => setIsModalOpen(true)}>Create Portal</Button>
    <Modal isOpen={isModalOpen} title="Create Portal" onClose={() => setIsModalOpen(false)}>
      <TextField label="Name" name="name" value={values.name} onChange={handleChange} />
      {/* More fields */}
    </Modal>
  </>
);
```

## 🐛 Debugging

### Enable Debug Logs
Add to `main.tsx`:
```tsx
if (process.env.NODE_ENV === 'development') {
  window.DEBUG = true;
}
```

### DevTools
- Use React DevTools browser extension
- Use Redux DevTools (if Redux added)
- Check Console for API errors

## 🎓 Best Practices

1. **Component Composition**: Break down large components into smaller, reusable ones
2. **Type Safety**: Always use TypeScript types, avoid `any`
3. **Error Handling**: Always handle API errors and edge cases
4. **Loading States**: Show loading indicators for async operations
5. **Accessibility**: Use semantic HTML and ARIA labels
6. **Performance**: Use keys in lists, memoize expensive operations
7. **Testing**: Test components and hooks (setup with Vitest)

## 📞 Support

For issues or questions about the frontend:
1. Check existing component examples
2. Review type definitions for API contracts
3. Check service/api.ts for available endpoints
4. Review component prop interfaces

---

**Last Updated**: 2024
**Version**: 0.2.0
