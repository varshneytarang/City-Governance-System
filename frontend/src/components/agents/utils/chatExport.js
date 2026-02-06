/**
 * Chat Export Utility
 * Exports chat history in various formats
 */

/**
 * Format timestamp for export
 */
const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

/**
 * Export chat as plain text
 */
export const exportAsText = (messages, agentName) => {
  const header = `Chat History - ${agentName}\nExported: ${formatTimestamp(new Date())}\n${'='.repeat(60)}\n\n`
  
  const messagesText = messages.map(msg => {
    const time = formatTimestamp(msg.timestamp)
    const sender = msg.type === 'user' ? 'You' : msg.type === 'agent' ? agentName : 'System'
    const content = msg.content
    
    return `[${time}] ${sender}:\n${content}\n`
  }).join('\n')
  
  return header + messagesText
}

/**
 * Export chat as JSON
 */
export const exportAsJSON = (messages, agentName) => {
  const exportData = {
    agent: agentName,
    exportDate: new Date().toISOString(),
    messageCount: messages.length,
    messages: messages.map(msg => ({
      id: msg.id,
      type: msg.type,
      content: msg.content,
      timestamp: msg.timestamp,
      status: msg.status,
      result: msg.result || null,
      jobId: msg.jobId || null
    }))
  }
  
  return JSON.stringify(exportData, null, 2)
}

/**
 * Export chat as Markdown
 */
export const exportAsMarkdown = (messages, agentName) => {
  const header = `# Chat History - ${agentName}\n\n**Exported:** ${formatTimestamp(new Date())}  \n**Messages:** ${messages.length}\n\n---\n\n`
  
  const messagesText = messages.map(msg => {
    const time = formatTimestamp(msg.timestamp)
    const sender = msg.type === 'user' ? '👤 **You**' : msg.type === 'agent' ? '🤖 **' + agentName + '**' : '⚙️ **System**'
    const content = msg.content
    
    return `### ${sender}\n*${time}*\n\n${content}\n\n---\n`
  }).join('\n')
  
  return header + messagesText
}

/**
 * Export chat as CSV
 */
export const exportAsCSV = (messages, agentName) => {
  const header = 'Timestamp,Sender,Message,Status\n'
  
  const rows = messages.map(msg => {
    const time = formatTimestamp(msg.timestamp)
    const sender = msg.type === 'user' ? 'User' : msg.type === 'agent' ? agentName : 'System'
    const content = `"${msg.content.replace(/"/g, '""')}"` // Escape quotes
    const status = msg.status || ''
    
    return `${time},${sender},${content},${status}`
  }).join('\n')
  
  return header + rows
}

/**
 * Export chat as HTML
 */
export const exportAsHTML = (messages, agentName, agentColor = '#3b82f6') => {
  const header = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chat History - ${agentName}</title>
  <style>
    body {
      font-family: system-ui, -apple-system, sans-serif;
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
      background: #f5f5f5;
    }
    .header {
      background: ${agentColor};
      color: white;
      padding: 20px;
      border-radius: 10px;
      margin-bottom: 20px;
    }
    .message {
      background: white;
      padding: 15px;
      margin: 10px 0;
      border-radius: 10px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .message.user {
      background: #e3f2fd;
      margin-left: 40px;
    }
    .message.agent {
      background: #f1f8e9;
      margin-right: 40px;
    }
    .message.system {
      background: #fff3e0;
      font-style: italic;
    }
    .timestamp {
      font-size: 0.75rem;
      color: #666;
      margin-bottom: 5px;
    }
    .sender {
      font-weight: bold;
      margin-bottom: 5px;
    }
    .content {
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>Chat History - ${agentName}</h1>
    <p>Exported: ${formatTimestamp(new Date())}</p>
    <p>Total Messages: ${messages.length}</p>
  </div>
  <div class="messages">`
  
  const messagesHTML = messages.map(msg => {
    const time = formatTimestamp(msg.timestamp)
    const sender = msg.type === 'user' ? 'You' : msg.type === 'agent' ? agentName : 'System'
    const content = msg.content.replace(/\n/g, '<br>')
    
    return `
    <div class="message ${msg.type}">
      <div class="timestamp">${time}</div>
      <div class="sender">${sender}</div>
      <div class="content">${content}</div>
    </div>`
  }).join('\n')
  
  const footer = `
  </div>
</body>
</html>`
  
  return header + messagesHTML + footer
}

/**
 * Download file with content
 */
export const downloadFile = (content, filename, mimeType = 'text/plain') => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Export chat in specified format
 */
export const exportChat = (messages, agentName, format = 'text', agentColor) => {
  const timestamp = new Date().toISOString().split('T')[0]
  const sanitizedAgentName = agentName.replace(/\s+/g, '_')
  
  let content, filename, mimeType
  
  switch (format) {
    case 'json':
      content = exportAsJSON(messages, agentName)
      filename = `chat_${sanitizedAgentName}_${timestamp}.json`
      mimeType = 'application/json'
      break
      
    case 'markdown':
    case 'md':
      content = exportAsMarkdown(messages, agentName)
      filename = `chat_${sanitizedAgentName}_${timestamp}.md`
      mimeType = 'text/markdown'
      break
      
    case 'csv':
      content = exportAsCSV(messages, agentName)
      filename = `chat_${sanitizedAgentName}_${timestamp}.csv`
      mimeType = 'text/csv'
      break
      
    case 'html':
      content = exportAsHTML(messages, agentName, agentColor)
      filename = `chat_${sanitizedAgentName}_${timestamp}.html`
      mimeType = 'text/html'
      break
      
    case 'text':
    default:
      content = exportAsText(messages, agentName)
      filename = `chat_${sanitizedAgentName}_${timestamp}.txt`
      mimeType = 'text/plain'
      break
  }
  
  downloadFile(content, filename, mimeType)
}

/**
 * Get chat statistics
 */
export const getChatStatistics = (messages) => {
  const stats = {
    total: messages.length,
    byType: {
      user: 0,
      agent: 0,
      system: 0
    },
    byStatus: {
      sent: 0,
      success: 0,
      error: 0,
      processing: 0
    },
    totalWords: 0,
    avgWordsPerMessage: 0,
    timeSpan: null
  }
  
  messages.forEach(msg => {
    // Count by type
    stats.byType[msg.type] = (stats.byType[msg.type] || 0) + 1
    
    // Count by status
    if (msg.status) {
      stats.byStatus[msg.status] = (stats.byStatus[msg.status] || 0) + 1
    }
    
    // Count words
    const words = msg.content.split(/\s+/).length
    stats.totalWords += words
  })
  
  stats.avgWordsPerMessage = messages.length > 0 
    ? Math.round(stats.totalWords / messages.length) 
    : 0
  
  // Calculate time span
  if (messages.length > 0) {
    const first = new Date(messages[0].timestamp)
    const last = new Date(messages[messages.length - 1].timestamp)
    const diffMs = last - first
    const diffMins = Math.round(diffMs / 60000)
    stats.timeSpan = diffMins > 60 
      ? `${Math.floor(diffMins / 60)}h ${diffMins % 60}m`
      : `${diffMins}m`
  }
  
  return stats
}

export default {
  exportChat,
  exportAsText,
  exportAsJSON,
  exportAsMarkdown,
  exportAsCSV,
  exportAsHTML,
  getChatStatistics,
  downloadFile
}
