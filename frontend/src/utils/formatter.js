// Message formatting utility

export function formatMessage(content) {
  if (!content) return ''

  let formatted = content

  // First, handle numbered lists with bold headers (e.g., "1. **Academic...**")
  // This pattern handles: "1. **Title**" or "1. Title:" format
  formatted = formatted.replace(/^(\d+)\.\s+\*\*(.+?)\*\*(.*)$/gim, '<li><strong>$2</strong>$3</li>')
  formatted = formatted.replace(/^(\d+)\.\s+(.+?):\s*(.*)$/gim, '<li><strong>$2:</strong> $3</li>')
  
  // Headers (## Header or ### Header) - do this before numbered lists
  formatted = formatted.replace(/^### (.*$)/gim, '<h3>$1</h3>')
  formatted = formatted.replace(/^## (.*$)/gim, '<h2>$1</h2>')
  formatted = formatted.replace(/^# (.*$)/gim, '<h1>$1</h1>')

  // Bold (**text** or __text__)
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  formatted = formatted.replace(/__(.*?)__/g, '<strong>$1</strong>')

  // Italic (*text* or _text_) - but not if it's part of bold
  formatted = formatted.replace(/(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
  formatted = formatted.replace(/(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)/g, '<em>$1</em>')

  // Links [text](url)
  formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')

  // Dates (format: YYYY-MM-DD or DD/MM/YYYY)
  formatted = formatted.replace(/\b(\d{4}-\d{2}-\d{2})\b/g, '<time>$1</time>')
  formatted = formatted.replace(/\b(\d{1,2}\/\d{1,2}\/\d{4})\b/g, '<time>$1</time>')

  // Split into lines for better processing
  const lines = formatted.split('\n')
  const processedLines = []
  let inList = false
  let listType = null
  let listItems = []

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    // Check for numbered list items (1. or 1) format)
    const numberedMatch = line.match(/^(\d+)[\.\)]\s+(.+)$/)
    // Check for bullet points (- or *)
    const bulletMatch = line.match(/^[\-\*]\s+(.+)$/)
    
    if (numberedMatch) {
      if (!inList || listType !== 'ol') {
        if (inList) {
          // Close previous list
          processedLines.push(`</${listType}>`)
        }
        processedLines.push('<ol>')
        inList = true
        listType = 'ol'
      }
      processedLines.push(`<li>${numberedMatch[2]}</li>`)
    } else if (bulletMatch) {
      if (!inList || listType !== 'ul') {
        if (inList) {
          // Close previous list
          processedLines.push(`</${listType}>`)
        }
        processedLines.push('<ul>')
        inList = true
        listType = 'ul'
      }
      processedLines.push(`<li>${bulletMatch[1]}</li>`)
    } else {
      // Not a list item
      if (inList) {
        processedLines.push(`</${listType}>`)
        inList = false
        listType = null
      }
      
      if (line) {
        // Check if it's already HTML (starts with <)
        if (line.startsWith('<')) {
          processedLines.push(line)
        } else {
          processedLines.push(`<p>${line}</p>`)
        }
      } else {
        // Empty line - add paragraph break
        if (processedLines.length > 0 && !processedLines[processedLines.length - 1].startsWith('<p>')) {
          processedLines.push('<br>')
        }
      }
    }
  }
  
  // Close any open list
  if (inList) {
    processedLines.push(`</${listType}>`)
  }

  formatted = processedLines.join('\n')

  // Clean up empty paragraphs
  formatted = formatted.replace(/<p>\s*<\/p>/g, '')
  formatted = formatted.replace(/<p><p>/g, '<p>')
  formatted = formatted.replace(/<\/p><\/p>/g, '</p>')

  return formatted
}

