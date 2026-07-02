import assert from 'node:assert/strict'
import { classifyPythonSubmitError } from '../app/api/analyze-text/python-submit'

assert.deepEqual(classifyPythonSubmitError({ name: 'AbortError' }), {
  kind: 'ack_timeout',
  httpStatus: 202,
  shouldMarkResourceFailed: false,
  clientMessage:
    'Analysis task was submitted, but the service acknowledgement timed out. Check the task list for the final status.',
  resourceErrorMessage: null
})

assert.deepEqual(classifyPythonSubmitError(new Error('connect ECONNREFUSED')), {
  kind: 'connection_error',
  httpStatus: 503,
  shouldMarkResourceFailed: true,
  clientMessage: 'Cannot connect to analysis service, ensure Python backend is reachable',
  resourceErrorMessage: 'Cannot connect to Python analysis service'
})

console.log('analyze-text submit error classification check passed')
