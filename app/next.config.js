const path = require("path");

module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  output: "standalone",
  experimental: {
    optimizePackageImports: ["@mantine/core", "@mantine/hooks"],
  },
  webpack: (config) => {
    const src = path.join(__dirname, "src");
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": src,
      "lib/auth": path.join(src, "lib", "auth"),
      "lib/api": path.join(src, "lib", "api"),
    };
    return config;
  },
};
