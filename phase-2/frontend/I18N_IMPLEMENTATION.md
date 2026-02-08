# Urdu Language Support Implementation - Complete Guide

## Status: Partially Complete

### ✅ Completed Files

1. **Translation Files**
   - `/phase-2/frontend/src/locales/en.json` - Complete English translations
   - `/phase-2/frontend/src/locales/ur.json` - Complete Urdu translations

2. **i18n Configuration**
   - `/phase-2/frontend/src/i18n/config.ts` - Locale configuration
   - `/phase-2/frontend/src/i18n/request.ts` - Request locale detection
   - `/phase-2/frontend/src/middleware.ts` - Next.js middleware for locale routing

3. **Tailwind Configuration**
   - `/phase-2/frontend/tailwind.config.ts` - Updated with RTL support utilities

4. **Next.js Configuration**
   - `/phase-2/frontend/next.config.ts` - Updated with next-intl plugin

5. **App Structure**
   - `/phase-2/frontend/src/app/layout.tsx` - Updated root layout (delegates to locale)
   - `/phase-2/frontend/src/app/[locale]/layout.tsx` - Locale-specific layout
   - `/phase-2/frontend/src/app/[locale]/page.tsx` - Landing page

6. **Components**
   - `/phase-2/frontend/src/components/layout/LanguageSwitcher.tsx` - Language switcher component
   - `/phase-2/frontend/src/components/layout/Header.tsx` - Updated with i18n support

### 🚧 Remaining Work

#### 1. Move and Update Pages to `[locale]` Directory

The following pages need to be moved from `/src/app/` to `/src/app/[locale]/` and updated with locale-aware links:

- [ ] `/src/app/login/page.tsx` → `/src/app/[locale]/login/page.tsx`
- [ ] `/src/app/signup/page.tsx` → `/src/app/[locale]/signup/page.tsx`
- [ ] `/src/app/chat/page.tsx` → `/src/app/[locale]/chat/page.tsx`
- [ ] `/src/app/(dashboard)/layout.tsx` → `/src/app/[locale]/(dashboard)/layout.tsx`
- [ ] `/src/app/(dashboard)/dashboard/page.tsx` → `/src/app/[locale]/(dashboard)/dashboard/page.tsx`
- [ ] `/src/app/test-env/page.tsx` → Can be removed (test only)

#### 2. Update All Hardcoded Strings

Replace hardcoded English strings with `useTranslations()` hook in the following files:

**Login Page** (`/src/app/[locale]/login/page.tsx`):
```tsx
// Add at top:
import { useTranslations } from 'next-intl';
const t = useTranslations('auth');

// Replace:
"Welcome Back" → {t('signIn')}
"Sign in to your account" → (use a new key)
"Email Address" → {t('email')}
"Password" → {t('password')}
"Forgot password?" → {t('forgotPassword')}
"Sign In" → {t('signIn')}
```

**Signup Page** (`/src/app/[locale]/signup/page.tsx`):
```tsx
// Add at top:
import { useTranslations } from 'next-intl';
const t = useTranslations('auth');

// Replace:
"Create Account" → {t('signUp')}
"Full Name" → {t('name')}
"Email Address" → {t('email')}
"Password" → {t('password')}
"Create Account" → {t('signUp')}
```

**Dashboard Page** (`/src/app/[locale]/(dashboard)/dashboard/page.tsx`):
```tsx
// Add at top:
import { useTranslations } from 'next-intl';
const t = useTranslations('tasks');

// Replace:
"My Tasks" → {t('title')}
"No tasks yet. Create one to get started!" → {t('noTasks')}
"Add Task" → {t('addTask')}
"Edit Task" → {t('edit')} (add to translation)
"Create New Task" → {t('addTask')}
"Update the task details below." → (add to translation)
```

**Chat Page** (`/src/app/[locale]/chat/page.tsx`):
```tsx
// Add at top:
import { useTranslations } from 'next-intl';
const t = useTranslations('chat');
```

#### 3. Update API Client and Library Files

Update links in API and library files to include locale:

- `/src/lib/api.ts` - No changes needed (API calls are absolute)
- `/src/lib/auth.ts` - Update redirect URLs to include locale

#### 4. Add Missing Translation Keys

Add these missing keys to both `en.json` and `ur.json`:

```json
{
  "auth": {
    "welcomeBack": "Welcome Back",
    "signInToAccount": "Sign in to your account to continue",
    "createAccount": "Create Account",
    "getStarted": "Get started with TaskFlow for free",
    "fullName": "Full Name",
    "signingIn": "Signing in...",
    "creatingAccount": "Creating account...",
    "continueWithGoogle": "Continue with Google",
    "agreeToTerms": "By creating an account, you agree to our",
    "termsOfService": "Terms of Service",
    "and": "and",
    "privacyPolicy": "Privacy Policy",
    "haveAccount": "Already have an account?",
    "noAccount": "Don't have an account?",
    "signIn": "Sign in",
    "signUpFree": "Sign up for free",
    "protectedBySecurity": "Protected by enterprise-grade security"
  },
  "tasks": {
    "editTask": "Edit Task",
    "createNewTask": "Create New Task",
    "updateTaskDetails": "Update the task details below.",
    "fillTaskDetails": "Fill in the details to create a new task.",
    "all": "All",
    "pending": "Pending",
    "completed": "Completed",
    "noTasksYet": "No tasks yet. Create one to get started!",
    "tasksCompleted": "tasks completed",
    "pendingTasks": "pending"
  }
}
```

#### 5. RTL Styling Adjustments

For Urdu (RTL), ensure proper styling by:

1. **Header Component** - Already updated with locale support
2. **Dashboard** - Check alignment of filters and task cards
3. **Forms** - Ensure input fields align correctly in RTL
4. **Dialogs** - Check positioning and padding

Use logical CSS properties:
- `margin-inline-start` instead of `margin-left`
- `margin-inline-end` instead of `margin-right`
- `padding-inline-start` instead of `padding-left`
- `padding-inline-end` instead of `padding-right`

#### 6. Test the Implementation

After completing all changes:

1. **Test English (default)**:
   - Visit `/` → should redirect to `/en`
   - All text displays in English

2. **Test Urdu**:
   - Visit `/ur` → should display Urdu text
   - Text should be right-to-left (RTL)
   - Layout should adjust correctly

3. **Test Language Switching**:
   - Click language switcher in header
   - URL should update to `/en/...` or `/ur/...`
   - Content should update to selected language
   - Current route should be preserved

4. **Test All Routes**:
   - `/en/login`, `/ur/login`
   - `/en/signup`, `/ur/signup`
   - `/en/dashboard`, `/ur/dashboard`
   - `/en/chat`, `/ur/chat`

### 🔧 Manual Steps Required

Since pnpm installation is still running, after it completes:

1. **Verify next-intl is installed**:
   ```bash
   cd phase-2/frontend
   pnpm list next-intl
   ```

2. **Create the remaining locale pages** by copying from existing pages:
   ```bash
   cp src/app/login/page.tsx src/app/[locale]/login/page.tsx
   cp src/app/signup/page.tsx src/app/[locale]/signup/page.tsx
   cp src/app/chat/page.tsx src/app/[locale]/chat/page.tsx
   cp src/app/(dashboard)/layout.tsx src/app/[locale]/(dashboard)/layout.tsx
   cp src/app/(dashboard)/dashboard/page.tsx src/app/[locale]/(dashboard)/dashboard/page.tsx
   ```

3. **Update each page** with `useTranslations()` and locale-aware links

4. **Test the application**:
   ```bash
   cd phase-2/frontend
   pnpm dev
   ```

5. **Verify in browser**:
   - Visit http://localhost:3000
   - Should redirect to http://localhost:3000/en
   - Click language switcher to test Urdu

### 📝 Notes

1. **URL Structure**: All URLs now include locale prefix: `/en/*`, `/ur/*`

2. **Default Locale**: Users are redirected to `/en` by default unless they have a cookie set

3. **Locale Detection**: Order of priority:
   - URL path (`/ur/...`)
   - Cookie (`NEXT_LOCALE`)
   - Accept-Language header
   - Default (`en`)

4. **RTL Support**: Tailwind utilities added for RTL styling:
   - `.rtl` / `.ltr` classes
   - Logical margin/padding utilities

5. **Performance**: next-intl uses automatic code splitting for locale files

### 🐛 Known Issues

1. **@tailwindcss/typography**: May need to be installed separately if not already present
2. **Old routes**: Old routes without locale (`/login`, `/dashboard`) will 404 after middleware is active
3. **API routes**: API routes are excluded from locale middleware (see `matcher` in middleware.ts)

### 🎯 Success Criteria

- [x] Translation files created (en.json, ur.json)
- [x] i18n configuration files created
- [x] Middleware for locale routing
- [x] Language switcher component
- [x] Header updated with i18n
- [x] Tailwind RTL utilities added
- [ ] All pages moved to [locale] directory
- [ ] All hardcoded strings replaced with translations
- [ ] RTL layout tested and working
- [ ] Language switching tested
- [ ] All routes tested with both locales

## Next Steps

1. Wait for pnpm installation to complete
2. Copy remaining pages to [locale] directory
3. Update pages with useTranslations() hooks
4. Update links to include locale
5. Test thoroughly with both English and Urdu
