/**
 * ErrorFallback - Displays error messages with retry options
 */
import './ErrorFallback.css';

export type ErrorType = 'network' | 'llm' | 'audio' | 'general';

interface Props {
  error?: Error | null;
  errorType?: ErrorType;
  onRetry?: () => void;
  onDismiss?: () => void;
}

function getErrorMessage(error: Error | null, errorType?: ErrorType): { title: string; message: string } {
  if (errorType === 'network' || error?.message?.includes('network') || error?.message?.includes('Network')) {
    return {
      title: 'Connection Error',
      message: "Can't reach server. Check your internet connection and try again."
    };
  }

  if (errorType === 'llm' || error?.message?.includes('LLM') || error?.message?.includes('AI')) {
    return {
      title: 'AI Service Unavailable',
      message: 'The AI service is temporarily unavailable. You can continue with the lesson.'
    };
  }

  if (errorType === 'audio' || error?.message?.includes('audio') || error?.message?.includes('Audio')) {
    return {
      title: 'Audio Error',
      message: 'Audio failed to load. You can continue without audio.'
    };
  }

  return {
    title: 'Something went wrong',
    message: error?.message || 'An unexpected error occurred. Please try again.'
  };
}

export default function ErrorFallback({ error, errorType, onRetry, onDismiss }: Props) {
  const { title, message } = getErrorMessage(error || null, errorType);
  const isMinorError = errorType === 'llm' || errorType === 'audio';

  return (
    <div className={`error-fallback ${isMinorError ? 'minor' : 'major'}`}>
      <div className="error-icon">
        {isMinorError ? '!' : '!'}
      </div>
      <h2 className="error-title">{title}</h2>
      <p className="error-message">{message}</p>
      <div className="error-actions">
        {onRetry && (
          <button className="retry-button" onClick={onRetry}>
            Try Again
          </button>
        )}
        {onDismiss && (
          <button className="dismiss-button" onClick={onDismiss}>
            {isMinorError ? 'Continue' : 'Go Back'}
          </button>
        )}
      </div>
    </div>
  );
}

export function InlineError({
  message,
  onRetry
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="inline-error">
      <span className="inline-error-message">{message}</span>
      {onRetry && (
        <button className="inline-retry-button" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}
