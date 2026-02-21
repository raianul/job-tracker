const path = require("path");

module.exports = {
  reactStrictMode: true,
  swcMinify: true,
  output: "standalone",
  experimental: {
    optimizePackageImports: ["@mantine/core", "@mantine/hooks"],
  },
  webpack: (config, { isServer }) => {
    config.resolve.alias["@"] = path.resolve(__dirname, "src");
    return config;
  },
};
