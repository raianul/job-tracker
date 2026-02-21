const path = require("path");

module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  output: "standalone",
  experimental: {
    optimizePackageImports: ["@mantine/core", "@mantine/hooks"],
  },
  webpack: (config) => {
    const srcDir = path.join(__dirname, "src");
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": srcDir,
    };
    // Resolve from src so "lib/api" and "lib/auth" work from any file (fixes Vercel)
    config.resolve.modules = [srcDir, "node_modules", ...(config.resolve.modules || [])];
    return config;
  },
};
