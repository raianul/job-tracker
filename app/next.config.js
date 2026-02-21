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
    const libDir = path.join(__dirname, "src", "lib");
    config.resolve.alias = {
      ...config.resolve.alias,
      "@": srcDir,
      "lib/api": path.join(libDir, "api"),
      "lib/auth": path.join(libDir, "auth"),
      lib: libDir,
    };
    return config;
  },
};
