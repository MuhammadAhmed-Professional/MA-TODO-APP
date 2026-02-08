# Check for Service Worker Interference

## In Browser DevTools:

### Step 1: Check Service Workers
1. Press **F12**
2. Go to **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Look for **Service Workers** in the left sidebar
4. **Screenshot** if any are registered
5. Click **Unregister** for each one
6. Refresh the page

### Step 2: Check if HTTP is in the Network Tab
1. Press **F12** → **Network** tab
2. Check **Disable cache** checkbox
3. Reload page (Ctrl + Shift + R)
4. Find the request to `/api/tasks/`
5. Click on it
6. Look at **Request URL** - is it HTTP or HTTPS?
7. **Screenshot the request details**

### Step 3: Check the fetchAPI Function
1. Press **F12** → **Console**
2. Type this and press Enter:
```javascript
console.log(window.location.protocol);
console.log(document.location.href);
```
3. **Copy the output**

### Step 4: Manual Test
1. In Console, type:
```javascript
fetch('https://tda-backend-production.up.railway.app/api/tasks/', {
  credentials: 'include',
  headers: {'Content-Type': 'application/json'}
}).then(r => console.log('Response:', r)).catch(e => console.log('Error:', e));
```
2. **Check if this works** (might get CORS error, but should be HTTPS)

### Step 5: Check Browser Extensions
1. **Disable ALL browser extensions**
2. Close and restart browser
3. Test again in incognito

---

## What to Report:

1. Are there any service workers registered?
2. What does the Network tab show for Request URL?
3. What browser are you using? (Chrome, Firefox, Edge, Brave?)
4. Does it work on your phone/different device?
