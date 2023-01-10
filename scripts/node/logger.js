import winston from "winston";

const log = winston.createLogger({
  level: "info",
  transports: [new winston.transports.Console()],
});

export { log };