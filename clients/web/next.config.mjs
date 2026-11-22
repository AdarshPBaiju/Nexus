/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@nexus/ui', '@nexus/contracts'],
  async rewrites() {
    const apiTarget = process.env.NEXUS_API_INTERNAL_URL || 'http://127.0.0.1:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiTarget}/api/:path*`,
      },
      {
        source: '/healthz',
        destination: `${apiTarget}/healthz`,
      },
    ];
  },
};

export default nextConfig;
