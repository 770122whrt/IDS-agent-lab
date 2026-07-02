export const PYTHON_API_TIMEOUT_MS = 10_000

type PythonSubmitErrorKind = 'ack_timeout' | 'connection_error'

type PythonSubmitErrorClassification = {
  kind: PythonSubmitErrorKind
  httpStatus: 202 | 503
  shouldMarkResourceFailed: boolean
  clientMessage: string
  resourceErrorMessage: string | null
}

function hasErrorName(error: unknown, name: string): boolean {
  return typeof error === 'object' && error !== null && 'name' in error && (error as { name?: unknown }).name === name
}

export function classifyPythonSubmitError(error: unknown): PythonSubmitErrorClassification {
  if (hasErrorName(error, 'AbortError')) {
    return {
      kind: 'ack_timeout',
      httpStatus: 202,
      shouldMarkResourceFailed: false,
      clientMessage:
        'Analysis task was submitted, but the service acknowledgement timed out. Check the task list for the final status.',
      resourceErrorMessage: null
    }
  }

  return {
    kind: 'connection_error',
    httpStatus: 503,
    shouldMarkResourceFailed: true,
    clientMessage: 'Cannot connect to analysis service, ensure Python backend is reachable',
    resourceErrorMessage: 'Cannot connect to Python analysis service'
  }
}
