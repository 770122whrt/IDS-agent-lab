import { NextResponse, type NextRequest } from 'next/server'
import { defaultLocale, isLocale, localeCookieName } from '@/i18n/config'

const PUBLIC_FILE = /\.(.*)$/

type RedirectOriginInput = {
  configuredAppUrl?: string
  currentOrigin: string
  forwardedHost: string | null
  forwardedProto: string | null
  host: string | null
  nodeEnv?: string
}

function shouldSkip(pathname: string): boolean {
  return (
    pathname.startsWith('/api') ||
    pathname.startsWith('/_next') ||
    pathname === '/favicon.ico' ||
    pathname === '/robots.txt' ||
    pathname === '/sitemap.xml' ||
    PUBLIC_FILE.test(pathname)
  )
}

function firstHeaderValue(value: string | null): string | null {
  return value?.split(',')[0]?.trim() || null
}

function isInternalHost(host: string | null): boolean {
  return !host || host.startsWith('localhost') || host.startsWith('127.0.0.1') || host.startsWith('[::1]')
}

function configuredOrigin(value: string | undefined): string | null {
  if (!value) {
    return null
  }

  try {
    return new URL(value).origin
  } catch {
    return null
  }
}

function protocolFromOrigin(origin: string): string {
  try {
    return new URL(origin).protocol.replace(':', '') || 'http'
  } catch {
    return 'http'
  }
}

export function resolveRedirectOrigin({
  configuredAppUrl,
  currentOrigin,
  forwardedHost,
  forwardedProto,
  host,
  nodeEnv
}: RedirectOriginInput): string {
  const selectedHost = firstHeaderValue(forwardedHost) ?? firstHeaderValue(host)
  const appOrigin = configuredOrigin(configuredAppUrl)

  if (nodeEnv === 'production' && isInternalHost(selectedHost) && appOrigin) {
    return appOrigin
  }

  if (selectedHost) {
    const protocol = firstHeaderValue(forwardedProto) ?? protocolFromOrigin(currentOrigin)
    return `${protocol}://${selectedHost}`
  }

  return appOrigin ?? currentOrigin
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  if (shouldSkip(pathname)) {
    return NextResponse.next()
  }

  const firstSegment = pathname.split('/')[1]
  if (isLocale(firstSegment)) {
    const response = NextResponse.next()
    response.cookies.set(localeCookieName, firstSegment, {
      path: '/',
      sameSite: 'lax'
    })
    return response
  }

  const cookieLocale = request.cookies.get(localeCookieName)?.value
  const locale = isLocale(cookieLocale) ? cookieLocale : defaultLocale
  const targetPathname = pathname === '/' ? `/${locale}` : `/${locale}${pathname}`
  const origin = resolveRedirectOrigin({
    configuredAppUrl: process.env.NEXT_PUBLIC_APP_URL ?? process.env.BETTER_AUTH_URL,
    currentOrigin: request.nextUrl.origin,
    forwardedHost: request.headers.get('x-forwarded-host'),
    forwardedProto: request.headers.get('x-forwarded-proto'),
    host: request.headers.get('host'),
    nodeEnv: process.env.NODE_ENV
  })
  const target = new URL(`${targetPathname}${request.nextUrl.search}`, origin)

  return NextResponse.redirect(target)
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)']
}
