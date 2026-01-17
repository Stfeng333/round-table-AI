import React from 'react'

const Button = ({ children, onClick, className = '' }) => {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 bg-white text-gray-900 font-medium rounded-md hover:bg-gray-100 transition-colors ${className}`}
    >
      {children}
    </button>
  )
}

export default Button
