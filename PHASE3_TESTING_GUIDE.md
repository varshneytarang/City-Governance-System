# Phase 3 Features - Quick Testing Guide

## 🚀 How to Test Phase 3 Features

### Prerequisites
1. Backend server running on `http://localhost:8000`
2. Frontend running on `http://localhost:3000`
3. Navigate to any agent page (e.g., `/agent/water`)

---

## ✅ Feature Testing Checklist

### 1. Smart Suggestions ✨
**Steps:**
1. Open chatbot sidebar
2. Click in the message input
3. Start typing: "Check water"
4. **Expected:** Suggestion dropdown appears with 3-5 relevant templates
5. Click on any suggestion
6. **Expected:** Message input populates with selected text
7. Press Enter to send

**Keyboard Test:**
- Type at least 2 characters to trigger suggestions
- Suggestions should update as you type
- Suggestions disappear when input is cleared

---

### 2. Message Search 🔍
**Steps:**
1. Send at least 5-10 messages in conversation
2. Click the Search icon (magnifying glass) in header
   - OR press `Ctrl+F` (Windows) / `Cmd+F` (Mac)
3. **Expected:** Search bar appears below header
4. Type a word that appears in a message (e.g., "water")
5. **Expected:** Counter shows "1/3" (result number/total)
6. Press `Enter` key to navigate to next result
7. Press `Shift+Enter` to go to previous result
8. Press `Esc` to close search

**Keyboard Test:**
- `Ctrl/Cmd+F` opens search
- `Enter` navigates forward
- `Shift+Enter` navigates backward
- `Esc` closes search bar

---

### 3. Chat Export 📥
**Steps:**
1. Have a conversation with at least 5 messages
2. Click the Download icon in header
3. **Expected:** Dropdown menu shows 5 format options
4. Click ".txt" format
5. **Expected:** File downloads immediately
6. Open downloaded file
7. **Expected:** See formatted chat with timestamps

**Test All Formats:**
- ✅ `.txt` - Plain text
- ✅ `.json` - JSON structure
- ✅ `.md` - Markdown with headers
- ✅ `.csv` - Spreadsheet format
- ✅ `.html` - Styled webpage (open in browser)

**Verify Export Contains:**
- Agent name in header
- Export timestamp
- All messages with timestamps
- Sender labels (You, Agent, System)
- Proper formatting for each format

---

### 4. Message Reactions & Copy 👍
**Steps:**
1. Send a message and wait for agent response
2. Hover your mouse over the **agent's response**
3. **Expected:** Action buttons appear on the side:
   - Copy button
   - Thumbs up button
   - Thumbs down button

**Test Copy:**
1. Click copy button
2. **Expected:** Button shows checkmark briefly
3. Paste text elsewhere
4. **Expected:** Message content is copied

**Test Reactions:**
1. Click thumbs up
2. **Expected:** Button turns green and stays highlighted
3. Click thumbs up again
4. **Expected:** Deselects (returns to normal)
5. Click thumbs down
6. **Expected:** Button turns red and stays highlighted
7. **Note:** Only agent messages have reaction buttons

---

### 5. Keyboard Shortcuts ⌨️
**Test Each Shortcut:**

| Shortcut | Expected Behavior | How to Test |
|----------|-------------------|-------------|
| `Enter` | Send message | Type message, press Enter |
| `Shift+Enter` | New line | Type message, press Shift+Enter, verify new line |
| `Ctrl/Cmd+F` | Open search | Press keys, search bar appears |
| `Ctrl/Cmd+K` | Clear chat | Press keys, confirmation dialog appears |
| `?` | Show help | Press ? key (input not focused), help modal opens |
| `Esc` | Close dialogs | Open search/help, press Esc, dialog closes |

---

### 6. Help System 💡
**Steps:**
1. Click the Help icon (?) in header
   - OR press `?` key when input is not focused
2. **Expected:** Help modal opens with:
   - Feature descriptions (6 features)
   - Keyboard shortcuts table
   - Pro tips section
3. Review features section
4. Check keyboard shortcuts
5. Click "Got it!" button or press Esc
6. **Expected:** Modal closes

**Verify Modal Content:**
- ✅ 6 feature cards with icons
- ✅ Keyboard shortcuts with visual keys
- ✅ Pro tips section with bullet points
- ✅ Contact information in footer

---

### 7. Enhanced Typing Indicators 💬
**Steps:**
1. Send a message
2. **Expected:** User message appears in blue bubble
3. Watch for processing indicator
4. **Expected:** Three pulsing dots with "Processing..." text
5. Wait for agent response
6. **Expected:** Agent message appears in gray bubble
7. Check timestamp below message
8. **Expected:** Shows time in format "10:30 AM"

**Status Icons:**
- ✅ Green checkmark = Success
- ✅ Red X = Error
- ✅ Yellow clock = Processing

---

### 8. Backend Connection Status 🌐
**Test Online Status:**
1. With backend running, check header
2. **Expected:** Green pulsing dot + "Online" label

**Test Offline Status:**
1. Stop backend server (`Ctrl+C` in backend terminal)
2. Wait 30 seconds (health check interval)
3. **Expected:** Red dot + "Offline" label
4. **Expected:** Warning banner appears: "Backend offline..."
5. Try sending message
6. **Expected:** Send button is disabled

**Recovery Test:**
1. Restart backend
2. Wait 30 seconds
3. **Expected:** Returns to "Online" status

---

## 🎯 Complete User Journey Test

**Scenario:** New user testing all features

1. **Open chatbot** → See welcome screen
2. **Type "Check w"** → Suggestions appear
3. **Select suggestion** → Input populated
4. **Send message** → Processing indicator shows
5. **Receive response** → Agent message appears
6. **Hover response** → Action buttons appear
7. **Click thumbs up** → Button highlights green
8. **Click copy** → Message copied
9. **Send 3 more messages** → Conversation builds
10. **Press Ctrl+F** → Search opens
11. **Search for "check"** → Results found
12. **Navigate results** → Counter updates
13. **Close search** → Press Esc
14. **Click Download** → Export menu opens
15. **Download .html** → File downloads
16. **Open file** → Formatted conversation appears
17. **Press ?** → Help modal opens
18. **Review features** → All 6 features listed
19. **Close help** → Click "Got it!"
20. **Press Ctrl+K** → Clear confirmation
21. **Cancel** → Chat preserved

---

## 🐛 Common Issues & Solutions

### Suggestions Not Appearing
- **Issue:** No dropdown when typing
- **Solution:** Type at least 2 characters
- **Check:** Console for errors in messageParser.js

### Search Not Finding Messages
- **Issue:** "No results" for existing text
- **Solution:** Search is case-insensitive, try single words
- **Check:** Ensure minimum 2 characters

### Export Not Downloading
- **Issue:** Click export but no file
- **Solution:** Check browser download settings/permissions
- **Check:** Console for blob/download errors

### Keyboard Shortcuts Not Working
- **Issue:** Keys don't trigger actions
- **Solution:** Ensure input field is not focused (except Shift+Enter)
- **Check:** Make sure you're using Ctrl (Windows) or Cmd (Mac)

### Reactions Not Showing
- **Issue:** No hover buttons on messages
- **Solution:** Only agent messages have reactions
- **Check:** Try hovering over agent (gray) messages, not user (blue) messages

### Backend Status Always Offline
- **Issue:** Red dot even with backend running
- **Solution:** 
  1. Check backend is on `http://localhost:8000`
  2. Check `/api/v1/health` endpoint works
  3. Wait 30 seconds for health check cycle

---

## 📊 Performance Expectations

- **Suggestion response:** < 50ms
- **Search results:** < 100ms
- **Export generation:** < 1s for 100 messages
- **Copy to clipboard:** Instant
- **Page load:** < 2s with history

---

## ✅ Final Verification

After testing all features:

- [ ] Smart suggestions work for all 6 agent types
- [ ] Search finds and navigates all messages
- [ ] Export works in all 5 formats
- [ ] Copy works on all messages
- [ ] Reactions persist when selected
- [ ] All keyboard shortcuts functional
- [ ] Help modal displays correctly
- [ ] Typing indicators show during processing
- [ ] Backend status updates accurately
- [ ] Chat history persists on page reload

---

## 🎉 Success Criteria

All Phase 3 features are working if:
1. ✅ Can type and see smart suggestions
2. ✅ Can search conversation history
3. ✅ Can export chat in any format
4. ✅ Can copy any message to clipboard
5. ✅ Can rate agent responses
6. ✅ Keyboard shortcuts respond correctly
7. ✅ Help system shows all features
8. ✅ Animations are smooth and responsive
9. ✅ No console errors
10. ✅ Works across all 6 agent types

---

**Happy Testing! 🚀**

If you encounter any issues, check:
1. Browser console for errors
2. Network tab for failed API calls
3. LocalStorage for saved chat data
4. React DevTools for component state
