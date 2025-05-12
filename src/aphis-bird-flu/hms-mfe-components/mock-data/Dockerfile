FROM node:20-alpine

# Create app directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source files
COPY . .

# Add health endpoint to server.js
RUN sed -i '/app.listen/i \
// Health endpoint\n\
app.get("/health", (req, res) => {\n\
  console.log("GET /health");\n\
  res.json({ status: "healthy" });\n\
});' server.js

# Expose port
EXPOSE 8000

# Start server
CMD ["node", "server.js"]