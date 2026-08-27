/** @type {import('next').NextConfig} */
const nextConfig = {
  // The FastAPI backend. In dev this is localhost:8000; production wiring
  // is deployment-config (env), never baked in.
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.API_URL ?? "http://localhost:8000"}/:path*`,
      },
    ];
  },
};

export default nextConfig;
