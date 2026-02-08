# Skill: Make Responsive

## Description
Add Tailwind CSS responsive classes to React components to ensure mobile-first responsive design across all breakpoints (mobile 320px+, tablet 768px+, desktop 1024px+).

## Inputs
- `component_file`: Path to the React component (e.g., `frontend/src/components/tasks/TaskList.tsx`)
- `breakpoint_requirements`: Responsive behavior for each breakpoint (e.g., "mobile: single column, tablet: 2 columns, desktop: 3 columns")

## Process

### 1. Analyze Current Component
- Read the component file
- Identify layout elements (divs, grids, flex containers)
- Identify spacing (margins, padding)
- Identify typography (font sizes, line heights)
- Identify visibility toggles (show/hide on different screens)

### 2. Apply Mobile-First Approach
Tailwind uses mobile-first breakpoints:
- Base styles = mobile (no prefix, applies to 0px+)
- `sm:` = tablet (640px+)
- `md:` = tablet landscape (768px+)
- `lg:` = desktop (1024px+)
- `xl:` = large desktop (1280px+)

**Pattern**:
```typescript
// Before (static)
<div className="grid grid-cols-3 gap-4">

// After (responsive)
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 md:gap-4">
```

### 3. Common Responsive Patterns

#### Grid Layouts
```typescript
// Single column mobile, 2 cols tablet, 3 cols desktop
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
```

#### Flexbox Layouts
```typescript
// Stack vertically on mobile, row on desktop
className="flex flex-col lg:flex-row gap-4"
```

#### Spacing
```typescript
// Smaller padding on mobile, larger on desktop
className="p-4 md:p-6 lg:p-8"
```

#### Typography
```typescript
// Smaller font on mobile, larger on desktop
className="text-sm md:text-base lg:text-lg"
```

#### Visibility
```typescript
// Hide on mobile, show on desktop
className="hidden lg:block"

// Show on mobile, hide on desktop
className="block lg:hidden"
```

### 4. Test Responsive Behavior
After applying changes:
- Test in browser DevTools at 375px (mobile), 768px (tablet), 1920px (desktop)
- Verify no horizontal scrolling at any breakpoint
- Verify text is readable (min 14px font size)
- Verify touch targets are ≥44px × 44px on mobile

## Example Usage

**Scenario**: Make TaskList component responsive

```bash
# Context: Task T076 from tasks.md
# T076: Update TaskList component with responsive grid (grid-cols-1 md:grid-cols-2 lg:grid-cols-3)
```

**Agent invocation**:
```
Make TaskList component responsive:
- Component: frontend/src/components/tasks/TaskList.tsx
- Requirements:
  - Mobile (320px-767px): Single column, full-width cards, 16px padding
  - Tablet (768px-1023px): 2-column grid, 24px padding
  - Desktop (1024px+): 3-column grid, 32px padding
```

**Scenario**: Make Header component responsive with mobile menu

```bash
# Context: Task T077 from tasks.md
# T077: Create responsive Header with hamburger menu for mobile, full nav for desktop
```

**Agent invocation**:
```
Make Header component responsive:
- Component: frontend/src/components/layout/Header.tsx
- Requirements:
  - Mobile: Hamburger menu icon, collapsible navigation drawer
  - Desktop: Full horizontal navigation bar
  - Use state to toggle mobile menu open/closed
```

## Constitution Compliance
- **Principle V**: Multi-interface - Responsive design ensures usability across devices
- **Principle II**: Clean code - Use Tailwind utility classes, no custom CSS
- **Principle XII**: Accessibility - Ensure touch targets meet minimum size (44px)

## Output
- Updated component file with responsive Tailwind classes
- Visual verification at mobile (375px), tablet (768px), desktop (1920px) viewports
