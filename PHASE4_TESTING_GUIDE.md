# Phase 4 Testing Guide - Quick Reference 🧪

## 🚀 Setup

1. **Install Dependencies** (if any new packages needed):
```bash
cd frontend
npm install
```

2. **Start Backend**:
```bash
python start_backend.py
```

3. **Start Frontend**:
```bash
cd frontend
npm run dev
```

4. **Open Browser**:
```
http://localhost:3000/agent/water
```

---

## ✅ Feature Testing

### 1. Error Boundary Testing 🛡️

**Test Scenario: Trigger Component Error**

**Option A: Manual Error Trigger (Dev Mode)**
1. Open browser DevTools Console
2. Type and execute:
```javascript
throw new Error('Test error boundary')
```
3. **Expected:** Error boundary UI appears
4. **Verify:**
   - ⚠️ Alert triangle icon
   - "Oops! Something Went Wrong" message
   - Error text displayed
   - Three buttons: "Try Again", "Reload Page", "Go to Home"

**Option B: Code Error (Temporary)**
Add to any component:
```jsx
if (true) throw new Error('Test error')
```

**Test Recovery Options:**
1. Click "Try Again" → Component resets
2. Click "Reload Page" → Full page refresh
3. Click "Go to Home" → Navigates to /

**Persistent Error Test:**
1. Make component throw error 3+ times
2. **Expected:** Error count increments
3. More drastic recovery options appear

**✅ Pass Criteria:**
- Error caught without crashing app
- Fallback UI renders correctly
- All recovery options work
- Error count tracked

---

### 2. Dark Mode Testing 🌙

**Steps:**
1. Locate Moon/Sun icon in chatbot header (next to Help button)
2. Click to toggle

**Light Mode → Dark Mode:**
- **Before:** White background, dark text
- **After:** Dark gray background (#1f2937), light text

**Verify Dark Mode Elements:**
- [ ] Chatbot sidebar: `bg-gray-900`
- [ ] Header: Dark background
- [ ] Messages: Adapted colors
- [ ] Input area: Dark theme
- [ ] Buttons: Dark hover states
- [ ] Search bar: Dark styling
- [ ] Help modal: Dark theme

**Persistence Test:**
1. Toggle dark mode ON
2. Refresh page (F5)
3. **Expected:** Stays in dark mode

**System Preference Test:**
1. Clear localStorage: `localStorage.clear()`
2. Set OS to dark mode
3. Refresh page
4. **Expected:** App loads in dark mode

**✅ Pass Criteria:**
- Toggle works smoothly
- All components update
- Preference persists across reloads
- System theme respected

---

### 3. Accessibility Testing ♿

**Keyboard Navigation:**
1. Unplug mouse (or promise not to use it!)
2. Press `Tab` key repeatedly
3. **Expected:** Blue focus ring moves through:
   - Quick action buttons
   - Search icon
   - Export icon
   - Help icon
   - Dark mode toggle
   - Message input
   - Send button
   - Clear button

**Tab Order Should Be:**
1. Quick Actions (if visible)
2. Header buttons (right to left)
3. Message input field
4. Send button
5. Clear button (if visible)

**Keyboard Shortcuts:**
| Key | Action | Expected |
|-----|--------|----------|
| `Tab` | Next element | Focus moves forward |
| `Shift+Tab` | Previous | Focus moves backward |
| `Enter` | Activate button | Button clicks |
| `Space` | Activate button | Button clicks |
| `?` | Help modal | Modal opens |
| `Ctrl+F` | Search | Search bar opens |
| `Esc` | Close | Modal/search closes |

**Screen Reader Test (if available):**
1. Enable NVDA (Windows) or VoiceOver (Mac)
2. Navigate chatbot
3. **Expected Announcements:**
   - "Chat interface region"
   - "Your message" / "Agent response"
   - "Message sent" (when sent)
   - "New message received" (when received)
   - "Processing your request" (during wait)
   - "Search messages button"

**ARIA Label Check:**
Open DevTools Elements panel, verify:
```html
<div role="region" aria-label="Chat interface">
<button aria-label="Send message">
<div role="article" aria-label="Your message">
<button aria-pressed="false" aria-label="Mark as helpful">
```

**✅ Pass Criteria:**
- All elements keyboard accessible
- Logical tab order
- Visible focus indicators
- Screen reader announces properly
- ARIA attributes present

---

### 4. Message Retry Testing 🔄

**Setup: Stop Backend**
```bash
# In backend terminal, press Ctrl+C
```

**Test Auto-Retry:**
1. Send message: "Test message"
2. **Expected:** Error message appears
3. Wait and observe:
   - "Retrying... (Attempt 1/3)" - Wait 1s
   - "Retrying... (Attempt 2/3)" - Wait 2s
   - "Retrying... (Attempt 3/3)" - Wait 4s
4. After 3 attempts: "❌ Failed to submit request after 3 attempts"

**Verify Exponential Backoff:**
- 1st retry: ~1 second delay
- 2nd retry: ~2 seconds delay
- 3rd retry: ~4 seconds delay

**Test Manual Retry:**
1. Wait for all auto-retries to fail
2. Locate red error message with "Retry" button
3. Click "Retry" button
4. **Expected:** Starts retrying again

**Test Recovery Mid-Retry:**
1. Send message (backend off)
2. After 1st retry, restart backend:
   ```bash
   python start_backend.py
   ```
3. **Expected:** Next retry succeeds
4. Retry counter resets to 0

**Check Notifications:**
- Toast appears: "Retrying message..."
- Toast shows on each retry attempt

**✅ Pass Criteria:**
- Auto-retries 3 times
- Exponential backoff timing correct
- Manual retry button appears
- Success resets counter
- Notifications show

---

### 5. Analytics Testing 📊

**View Analytics:**
1. Open DevTools Console
2. Type: `localStorage`
3. Look for keys starting with `analytics_water-`

**Check Session Data:**
```javascript
// In DevTools Console
const keys = Object.keys(localStorage).filter(k => k.startsWith('analytics_'))
const sessionData = JSON.parse(localStorage.getItem(keys[0]))
console.log(sessionData)
```

**Expected Structure:**
```javascript
{
  sessionId: "water-1707235200-abc123",
  agentType: "water",  
  startTime: 1707235200000,
  events: [
    {
      eventName: "session_started",
      timestamp: "2026-02-06T10:30:00.000Z",
      data: {}
    },
    {
      eventName: "message_sent",
      timestamp: "2026-02-06T10:30:15.000Z",
      data: {
        messageLength: 45,
        wordCount: 8
      }
    }
    // ... more events
  ]
}
```

**Test Event Tracking:**

| Action | Expected Event | Verify |
|--------|---------------|--------|
| Open chatbot | `session_started` | ✓ |
| Send message | `message_sent` | Check messageLength, wordCount |
| Receive response | `message_received` | Check duration |
| Click Search | `feature_used` | feature: 'search' |
| Export chat | `chat_exported` | Check format, messageCount |
| Thumbs up | `message_reaction` | reactionType: 'positive' |
| Use suggestion | `suggestion_used` | Check suggestion text |
| Clear chat | `chat_cleared` | Check messageCount |

**Get Metrics in Console:**
```javascript
// Access analytics from window (for testing)
// Note: In production, this is internal to the component
```

**✅ Pass Criteria:**
- Events logged to localStorage
- All actions tracked
- Session data persists
- Metrics calculated correctly

---

### 6. Performance Testing ⚡

**Measure Load Time:**
1. Open DevTools Network tab
2. Refresh page (Ctrl+R)
3. Check "DOMContentLoaded" time
4. **Expected:** < 2 seconds

**Test Message Rendering:**
1. Send 10 messages quickly
2. Observe scroll smoothness
3. **Expected:** No lag, 60fps

**Test Debounced Suggestions:**
1. Type in message input: "Check wa"
2. **Don't pause** - type continuously
3. Stop typing
4. **Expected:** Suggestions appear 300ms after you stop

**Test Throttled Scroll:**
1. Have 50+ messages (use quick actions repeatedly)
2. Scroll rapidly up and down
3. **Expected:** Smooth scrolling, no jank

**Check Performance Metrics (DevTools):**
1. Open Performance tab
2. Click Record (red circle)
3. Interact with chatbot (send messages, scroll)
4. Stop recording
5. **Verify:**
   - FPS stays near 60
   - No long tasks (yellow/red blocks)
   - Scripting time < 50ms per frame

**Memory Test:**
1. Open DevTools Memory tab
2. Take heap snapshot
3. Send 100 messages
4. Take another snapshot
5. Compare
6. **Expected:** No significant memory leaks

**✅ Pass Criteria:**
- Initial load < 2s
- 60fps animations
- No lag during typing
- Smooth scrolling
- Memory stable

---

### 7. Notification System Testing 🔔

**Test Success Notification:**
1. Send message successfully
2. **Expected:** No toast (messages use inline status)

**Test Export Notification:**
1. Send a few messages
2. Click Download → Select .txt
3. **Expected:** Green toast appears:
   - ✓ Checkmark icon
   - "Chat exported as .txt"
   - Auto-dismisses after 3s

**Test Clear Notification:**
1. Click Clear chat (trash icon)
2. Confirm dialog
3. **Expected:** Blue info toast:
   - ℹ Info icon
   - "Conversation cleared"
   - Auto-dismisses after 2s

**Test Error Notification:**
1. Stop backend
2. Send message
3. Wait for retries to fail
4. **Expected:** Red error toast:
   - ✗ Error icon
   - "Failed to submit request..."
   - Longer duration (7s)

**Test Manual Dismiss:**
1. Trigger any notification
2. Click X button on toast
3. **Expected:** Notification disappears immediately

**Test Stacking:**
1. Rapidly trigger multiple notifications:
   - Export chat (.txt)
   - Export chat (.json)
   - Export chat (.md)
2. **Expected:** 3 toasts stack vertically
3. Each dismisses independently

**Test Positioning:**
- Notifications appear top-right corner
- Don't overlap chatbot
- Stay on-screen when scrolling

**✅ Pass Criteria:**
- All notification types work
- Correct colors and icons
- Auto-dismiss timing works
- Manual dismiss works
- Multiple toasts stack properly

---

## 🎯 Integration Testing

**Full User Journey with Phase 4:**

1. **Start** → Open chatbot
   - Dark mode button visible
   - Help button visible
   - Analytics tracks session_started

2. **Toggle Dark Mode** → Click moon icon
   - Interface switches to dark theme
   - Preference saved

3. **Accessibility** → Navigate with keyboard
   - Tab through all elements
   - Focus visible on each

4. **Send Message** → Type and send
   - Suggestion appears while typing (debounced)
   - Message sent
   - Analytics tracks message_sent
   - Screen reader announces "Message sent"

5. **Receive Response** → Wait for agent
   - Processing indicator shows
   - Response appears
   - Analytics tracks message_received
   - Screen reader announces "New message received"

6. **React to Message** → Hover and thumbs up
   - Action buttons appear
   - Thumbs up highlights green
   - Analytics tracks message_reaction

7. **Test Retry** → Stop backend, send message
   - Auto-retries 3 times
   - Manual retry button appears
   - Notification shows retry status

8. **Search** → Press Ctrl+F
   - Search bar opens
   - Type query
   - Results found

9. **Export** → Click download icon
   - Select .json format
   - File downloads
   - Success notification appears
   - Analytics tracks chat_exported

10. **Error** → Trigger error (if possible)
    - Error boundary catches it
    - Fallback UI appears
    - Can recover

11. **Clear** → Clear chat
    - Confirmation dialog
    - Confirm
    - Info notification
    - Analytics tracks chat_cleared

12. **Close** → Close browser tab
    - Analytics tracks session_ended
    - Session saved to localStorage

**✅ All Features Working Together!**

---

## 🐛 Troubleshooting

### Dark Mode Not Persisting
**Solution:** Check localStorage:
```javascript
localStorage.getItem('darkMode') // Should be 'true' or 'false'
```

### Screen Reader Silent
**Solution:** 
- Verify browser allows screen reader API
- Check announcements element exists:
  ```javascript
  document.querySelectorAll('[aria-live]')
  ```

### Analytics Not Tracking
**Solution:** Check console for errors:
```javascript
// Should see analytics reference
console.log(analyticsRef.current)
```

### Notifications Not Showing
**Solution:** Verify NotificationProvider wraps app:
```jsx
<NotificationProvider>
  <DarkModeProvider>
    <App />
  </DarkModeProvider>
</NotificationProvider>
```

### Retry Not Working
**Solution:** Backend must be actively refusing connections (not just slow)

---

## 📋 Quick Checklist

Print this and check off as you test:

**Error Boundary:**
- [ ] Catches component errors
- [ ] Shows fallback UI
- [ ] Try Again works
- [ ] Reload Page works
- [ ] Go to Home works

**Dark Mode:**
- [ ] Toggle switches theme
- [ ] Preference persists
- [ ] System theme respected
- [ ] All components adapt

**Accessibility:**
- [ ] Full keyboard navigation
- [ ] Focus indicators visible
- [ ] Screen reader compatible
- [ ] ARIA labels present
- [ ] Logical tab order

**Retry:**
- [ ] Auto-retries 3 times
- [ ] Exponential backoff
- [ ] Manual retry button
- [ ] Success resets counter

**Analytics:**
- [ ] Session tracked
- [ ] Events logged
- [ ] Metrics calculated
- [ ] Data persists

**Performance:**
- [ ] Load < 2s
- [ ] Smooth 60fps
- [ ] No memory leaks
- [ ] Debouncing works

**Notifications:**
- [ ] Success toasts
- [ ] Error toasts
- [ ] Info toasts
- [ ] Auto-dismiss
- [ ] Manual dismiss
- [ ] Stacking works

---

## ✅ Definition of Done

Phase 4 is complete when:
- ✅ All 7 features fully tested
- ✅ No console errors
- ✅ Accessibility score 90+ (Lighthouse)
- ✅ Performance score 85+ (Lighthouse)
- ✅ Works in Chrome, Firefox, Safari, Edge
- ✅ Mobile responsive
- ✅ All documentation complete

---

**Happy Testing! 🎉**

Report Issues: support@citygovern.ai  
Documentation: PHASE4_POLISH_COMPLETE.md
