import React from 'react'

const Button = ({ children, onClick, disabled, className = '' }) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-6 py-3 bg-amber-500 text-neutral-900 font-bold rounded hover:bg-amber-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
    >
      {children}
    </button>
  )
}

export default Button
