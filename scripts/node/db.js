import crypto from "crypto";
import pkg from "pg";
const { Pool } = pkg;

let connString =
  "postgresql://meneame:gcy9U4IRzTdl@restless-meadow-475114.cloud.neon.tech:5432/mnm?ssl=true";

const pool = new Pool({
  connectionString: connString,
  keepAlive: true,
  idleTimeoutMillis: 5000,
});

pool.on("error", (err) => {
  console.error("Error", err.message, err.stack);
});

async function query(text, params) {
  const res = await pool.query(text, params);
  return res;
}

const sqlQuery = `
INSERT
	INTO comments(
    comment_md5_id,
    news_id,
    comment_text,
    votes_positive,
    votes_negative,
    url_full,
    updated_at
  )
VALUES ($1, $2, $3, $4, $5, $6, $7)
RETURNING *
`;

export async function upsertComments(comments, newsId, urlFull) {
  console.log("========= upsertComments");
  console.log(comments);
  console.log(newsId);
  console.log(urlFull);

  for (let i = 0; i < comments.length; i++) {
    try {
      const currentTime = new Date();

      const hash = crypto.createHash("md5");
      hash.update(comments[i].comment);
      const hashDigest = hash.digest("hex");

      const values = [
        hashDigest,
        newsId,
        comments[i].comment,
        comments[i].votes_positive,
        comments[i].votes_negative,
        urlFull,
        currentTime.toISOString(),
      ];
      const res = await query(sqlQuery, values);
      console.log(res.rows[0]);
    } catch (err) {
      console.log(err);
    }
  }
}