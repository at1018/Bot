import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './ChatMessage.css';

/**
 * ChatMessage Component
 * Renders markdown content with syntax highlighting for code blocks
 * Supports:
 * - Headings (##, ###, etc.)
 * - Lists (ordered and unordered)
 * - Bold, italic, and inline code
 * - Code blocks with language detection and syntax highlighting
 */
export const ChatMessage = ({ content, isUser }) => {
  const components = {
    // Code block renderer with syntax highlighting
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';

      // Inline code
      if (inline) {
        return (
          <code className="inline-code" {...props}>
            {children}
          </code>
        );
      }

      // Code block
      return (
        <div className="code-block-wrapper">
          {language && <div className="code-language-label">{language}</div>}
          <SyntaxHighlighter
            language={language || 'text'}
            style={oneDark}
            customStyle={{
              margin: 0,
              padding: '12px 16px',
              borderRadius: '0 0 8px 8px',
              fontSize: '13px',
              lineHeight: '1.5',
            }}
            showLineNumbers={language ? true : false}
            wrapLongLines={true}
          >
            {String(children).replace(/\n$/, '')}
          </SyntaxHighlighter>
        </div>
      );
    },

    // Heading styles
    h1: ({ children }) => <h1 className="markdown-heading markdown-h1">{children}</h1>,
    h2: ({ children }) => <h2 className="markdown-heading markdown-h2">{children}</h2>,
    h3: ({ children }) => <h3 className="markdown-heading markdown-h3">{children}</h3>,
    h4: ({ children }) => <h4 className="markdown-heading markdown-h4">{children}</h4>,

    // List styles
    ul: ({ children }) => <ul className="markdown-list markdown-ul">{children}</ul>,
    ol: ({ children }) => <ol className="markdown-list markdown-ol">{children}</ol>,
    li: ({ children }) => <li className="markdown-li">{children}</li>,

    // Paragraph with proper spacing
    p: ({ children }) => <p className="markdown-paragraph">{children}</p>,

    // Emphasis (bold/italic)
    strong: ({ children }) => <strong className="markdown-strong">{children}</strong>,
    em: ({ children }) => <em className="markdown-em">{children}</em>,

    // Blockquote
    blockquote: ({ children }) => (
      <blockquote className="markdown-blockquote">{children}</blockquote>
    ),

    // Horizontal rule
    hr: () => <hr className="markdown-hr" />,

    // Links
    a: ({ href, children }) => (
      <a href={href} target="_blank" rel="noopener noreferrer" className="markdown-link">
        {children}
      </a>
    ),
  };

  return (
    <div className={`chat-message-content ${isUser ? 'markdown-user' : 'markdown-bot'}`}>
      <ReactMarkdown components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
};
