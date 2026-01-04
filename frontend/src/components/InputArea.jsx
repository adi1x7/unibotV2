import React from 'react'

function InputArea({ value, onChange, onKeyPress, onSend, disabled }) {
  return (
    <footer className="input-area">
      <div className="input-container">
        <input
          type="text"
          id="messageInput"
          value={value}
          onChange={onChange}
          onKeyPress={onKeyPress}
          placeholder="Ask about fees, admissions, academics..."
          disabled={disabled}
        />
        <button id="sendButton" onClick={onSend} disabled={disabled}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </footer>
  )
}

export default InputArea

