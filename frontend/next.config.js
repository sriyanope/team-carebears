/** @type {import('next').NextConfig} */
const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

module.exports = {
  async rewrites() {
    return [
      { source: '/api/:path*', destination: `${apiBaseUrl}/api/:path*` },
    ]
  },
}
