# Skill: Create React Component (Next.js)

## Description
Generates a reusable React component for Next.js projects with TypeScript, type safety, accessibility features (ARIA labels, semantic HTML), responsive design using Tailwind CSS, and comprehensive JSDoc comments.

## Inputs
- **component_name**: PascalCase component name (e.g., "TaskCard", "LoginForm")
- **component_type**: Type (functional, form, layout, modal, card)
- **props_schema**: Object properties with types and defaults
- **children**: Boolean - does component accept children?
- **hooks**: List of React hooks needed (useState, useEffect, useContext, etc.)
- **features**: List of features (animations, responsive, interactive, etc.)
- **file_path**: Where to create (e.g., "frontend/src/components/tasks/TaskCard.tsx")
- **styling**: Tailwind CSS class suggestions for responsive design

## Process

1. **Validate Component Structure**
   - Component name must be PascalCase
   - Props must have TypeScript interfaces
   - Identify any custom hooks needed

2. **Generate Component Template**
   ```typescript
   'use client'; // Client Component if interactive

   import React from 'react';
   import { ComponentType } from '@/types';

   /**
    * [Component Description]
    *
    * Features:
    * - [Feature 1]
    * - [Feature 2]
    *
    * Accessibility:
    * - Keyboard navigation support
    * - ARIA labels for screen readers
    * - Semantic HTML structure
    *
    * @component
    * @example
    * ```tsx
    * <ComponentName prop1="value" />
    * ```
    */

   interface ComponentNameProps {
     // Props definition
   }

   export function ComponentName({
     prop1,
     prop2,
   }: ComponentNameProps): React.ReactElement {
     return (
       <div className="responsive-classes">
         {/* Component content */}
       </div>
     );
   }
   ```

3. **Add Type Safety**
   - Define TypeScript interfaces for all props
   - Use extracted types from `@/types`
   - Add default props where applicable
   - Provide proper return type annotations

4. **Add Accessibility Features**
   - Use semantic HTML (button, form, section, etc.)
   - Add aria-label for icon buttons
   - Add aria-describedby for descriptions
   - Ensure focus indicators for interactive elements
   - Keyboard navigation support (Tab, Enter, Escape)

5. **Add Responsive Design**
   - Mobile-first approach (no prefix = mobile)
   - Tailwind breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
   - Example: `flex flex-col md:flex-row lg:grid-cols-3`

6. **Component Organization**
   - Separate into modular parts if >200 lines
   - Extract complex logic into custom hooks
   - Keep styling in component file (inline Tailwind)
   - Place in appropriate folder (components/auth/, components/tasks/, etc.)

## Example Usage
```
/skill create-react-component \
  --component_name TaskCard \
  --component_type card \
  --props_schema "id:string, title:string, description:string, isComplete:boolean" \
  --features "toggle-complete,edit-button,delete-button,responsive" \
  --file_path frontend/src/components/tasks/TaskCard.tsx
```

## Output
- Complete React component with TypeScript
- Accessible and responsive design
- Ready to use in Next.js pages
- Can be composed with other components
- Includes JSDoc documentation

## File Structure Example
```
frontend/src/components/
├── ui/                    # shadcn/ui components
├── auth/                  # Auth-specific (LoginForm, SignupForm)
├── tasks/                 # Task components (TaskCard, TaskList, TaskForm)
└── layout/                # Layout (Header, Sidebar, Footer)
```
