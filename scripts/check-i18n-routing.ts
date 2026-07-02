import assert from 'node:assert/strict'
import { defaultLocale } from '../i18n/config'
import { getLocaleFromPath, splitLocalePath, switchLocalePath, withLocale } from '../i18n/routing'
import { resolveRedirectOrigin } from '../middleware'

assert.equal(defaultLocale, 'zh')

assert.deepEqual(splitLocalePath('/zh/tasks/123'), {
  locale: 'zh',
  pathWithoutLocale: '/tasks/123'
})

assert.deepEqual(splitLocalePath('/en'), {
  locale: 'en',
  pathWithoutLocale: '/'
})

assert.deepEqual(splitLocalePath('/dashboard'), {
  locale: null,
  pathWithoutLocale: '/dashboard'
})

assert.equal(withLocale('/dashboard', 'zh'), '/zh/dashboard')
assert.equal(withLocale('/en/tasks', 'zh'), '/zh/tasks')
assert.equal(withLocale('/', 'en'), '/en')
assert.equal(switchLocalePath('/zh/tasks', 'en', '?tab=report'), '/en/tasks?tab=report')
assert.equal(getLocaleFromPath('/en/sign-in'), 'en')
assert.equal(getLocaleFromPath('/sign-in'), 'zh')

assert.equal(
  resolveRedirectOrigin({
    configuredAppUrl: 'https://ids.example.com',
    currentOrigin: 'http://localhost:3000',
    forwardedHost: null,
    forwardedProto: null,
    host: 'localhost:3000',
    nodeEnv: 'production'
  }),
  'https://ids.example.com'
)

assert.equal(
  resolveRedirectOrigin({
    configuredAppUrl: 'https://ids.example.com',
    currentOrigin: 'http://localhost:3000',
    forwardedHost: null,
    forwardedProto: null,
    host: 'localhost:3000',
    nodeEnv: 'development'
  }),
  'http://localhost:3000'
)

assert.equal(
  resolveRedirectOrigin({
    configuredAppUrl: 'https://ids.example.com',
    currentOrigin: 'http://127.0.0.1:3000',
    forwardedHost: 'app.example.com',
    forwardedProto: 'https',
    host: '127.0.0.1:3000',
    nodeEnv: 'production'
  }),
  'https://app.example.com'
)

assert.equal(
  resolveRedirectOrigin({
    configuredAppUrl: 'http://120.27.163.126:8080',
    currentOrigin: 'http://127.0.0.1:3000',
    forwardedHost: '120.27.163.126',
    forwardedProto: 'http',
    host: '120.27.163.126',
    nodeEnv: 'production'
  }),
  'http://120.27.163.126:8080'
)

console.log('i18n routing check passed')
