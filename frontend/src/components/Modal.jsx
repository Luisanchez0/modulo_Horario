import React from 'react'

export default function Modal({ title, titleId, children, actions, onClose }) {
  return (
    <div className="calendar-modal-backdrop" role="presentation" onClick={onClose}>
      <div className="calendar-modal" role="dialog" aria-modal="true" aria-labelledby={titleId} onClick={(e) => e.stopPropagation()}>
        {title && <h4 id={titleId}>{title}</h4>}
        <div>
          {children}
        </div>
        {actions && <div className="calendar-modal-actions">{actions}</div>}
      </div>
    </div>
  )
}
