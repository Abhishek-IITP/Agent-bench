import postgres from "postgres";

const connectionString =
  process.env.DATABASE_URL ||
  process.env.POSTGRES_URL ||
  "postgresql://neondb_owner:npg_w2inPyHKQq9W@ep-cold-paper-aek12awj-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require";

export const sql = postgres(connectionString, {
  ssl: "require",
  max: 10,
  idle_timeout: 20,
});
