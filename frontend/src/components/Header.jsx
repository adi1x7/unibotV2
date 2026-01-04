import React from 'react'

function Header({ backendStatus }) {
  const statusStyle = {
    background: backendStatus.online ? '#d1fae5' : '#fee2e2',
    color: backendStatus.online ? '#065f46' : '#991b1b'
  }

  return (
    <header className="header">
      <div className="header-left">
        <div className="logo">
          <div className="logo-icon">🤖</div>
        </div>
        <div className="header-text">
          <h1>UniBot</h1>
          <p>BMSIT College AI Assistant</p>
        </div>
      </div>
      <div className="header-right">
        <div className="status-indicator" style={statusStyle}>
          <span className="status-dot"></span>
          <span>{backendStatus.text}</span>
        </div>
      </div>
    </header>
  )
}

export default Header

