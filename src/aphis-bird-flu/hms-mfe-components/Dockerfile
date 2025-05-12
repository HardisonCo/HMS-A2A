FROM bitnami/node:20 AS build

# Set working directory
WORKDIR /app

# Copy HMS-MFE source code
COPY hms-mfe/ .

# Copy APHIS components into HMS-MFE
COPY aphis-components/hms-mfe-components/*.vue ./src/components/aphis/
COPY aphis-components/hms-mfe-components/tabs/*.vue ./src/components/aphis/tabs/
COPY aphis-components/hms-mfe-components/composables/*.js ./src/composables/aphis/
COPY aphis-components/hms-mfe-components/index.js ./src/components/aphis/index.js

# Copy routes configuration
COPY aphis-components/hms-mfe-components/aphis.routes.js ./src/router/

# Environment variables for the build
ARG VITE_API_BASE_URL
ARG VITE_MAPBOX_ACCESS_TOKEN
ARG VITE_FEDERATION_HUB_URL

# Install dependencies and build
RUN corepack enable && corepack prepare pnpm@latest --activate
RUN pnpm install
RUN pnpm add axios mapbox-gl apexcharts vue3-apexcharts force-graph d3

# Add import to main.ts or main.js if it doesn't exist
RUN grep -q "registerComponents" src/app.ts || \
    sed -i '/createApp/a import { registerComponents } from "./components/aphis";' src/app.ts
RUN grep -q "registerComponents(app)" src/app.ts || \
    sed -i '/app.use(router)/a registerComponents(app);' src/app.ts

# Build the application
RUN VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_MAPBOX_ACCESS_TOKEN=$VITE_MAPBOX_ACCESS_TOKEN \
    VITE_FEDERATION_HUB_URL=$VITE_FEDERATION_HUB_URL \
    NODE_OPTIONS=--max-old-space-size=6144 \
    pnpm ssr:build

# Production stage
FROM bitnami/node:20 AS prod

# Set working directory
WORKDIR /app

# Install production dependencies only
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY --from=build /app/package.json ./
RUN pnpm install --prod

# Copy build artifacts
COPY --from=build /app/dist ./dist
COPY --from=build /app/server ./server

# Copy APHIS Bird Flu mock API server for development
COPY aphis-components/hms-mfe-components/mock-data ./mock-data
RUN cd mock-data && npm install

# Expose ports for the SSR application and mock API
EXPOSE 3000 8000

# Set environment to production
ENV NODE_ENV=production

# Start the SSR application and mock API server
CMD ["sh", "-c", "cd mock-data && node server.js & pnpm ssr:start"]