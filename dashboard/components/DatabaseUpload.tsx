"use client";

import { useState, useCallback } from "react";
import { Upload, AlertCircle } from "lucide-react";
import initSqlJs from "sql.js";

interface Props {
  onDataLoaded: (data: any) => void;
}

export default function DatabaseUpload({ onDataLoaded }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const parseDatabase = async (file: File) => {
    setIsLoading(true);
    setError(null);

    try {
      const SQL = await initSqlJs({
        locateFile: (file) => `https://sql.js.org/dist/${file}`,
      });

      const arrayBuffer = await file.arrayBuffer();
      const db = new SQL.Database(new Uint8Array(arrayBuffer));

      // Extract snapshots
      const snapshotsResult = db.exec(
        "SELECT * FROM snapshots ORDER BY timestamp DESC"
      );

      const snapshots = snapshotsResult[0]?.values.map((row) => ({
        id: row[0],
        timestamp: row[1],
        source: row[2],
        follower_count: row[3],
        following_count: row[4],
      })) || [];

      // Extract accounts
      const accountsResult = db.exec("SELECT * FROM accounts");
      const accounts = accountsResult[0]?.values.map((row) => ({
        pk: row[0],
        username: row[1],
        full_name: row[2],
        first_seen: row[3],
        last_seen: row[4],
      })) || [];

      // Get latest snapshot details
      let latestSnapshot = null;
      if (snapshots.length > 0) {
        const latestId = snapshots[0].id;

        const followersResult = db.exec(`
          SELECT a.username, a.full_name
          FROM snapshot_followers sf
          JOIN accounts a ON sf.account_pk = a.pk
          WHERE sf.snapshot_id = ${latestId}
        `);

        const followingResult = db.exec(`
          SELECT a.username, a.full_name
          FROM snapshot_following sf
          JOIN accounts a ON sf.account_pk = a.pk
          WHERE sf.snapshot_id = ${latestId}
        `);

        latestSnapshot = {
          ...snapshots[0],
          followers: followersResult[0]?.values.map((row) => ({
            username: row[0],
            full_name: row[1],
          })) || [],
          following: followingResult[0]?.values.map((row) => ({
            username: row[0],
            full_name: row[1],
          })) || [],
        };
      }

      // Get verification queue
      const verificationResult = db.exec(`
        SELECT vq.status, COUNT(*) as count
        FROM verification_queue vq
        GROUP BY vq.status
      `);

      const verification = verificationResult[0]?.values.reduce((acc, row) => {
        acc[row[0] as string] = row[1] as number;
        return acc;
      }, {} as Record<string, number>) || {};

      db.close();

      onDataLoaded({
        snapshots,
        accounts,
        latestSnapshot,
        verification,
      });
    } catch (err: any) {
      console.error("Database parsing error:", err);
      setError(err.message || "Failed to parse database. Make sure it's a valid instagram_audit.db file.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const file = e.dataTransfer.files[0];
    if (file) {
      if (file.name.endsWith(".db") || file.name.endsWith(".sqlite")) {
        parseDatabase(file);
      } else {
        setError("Please upload a .db or .sqlite file");
      }
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      parseDatabase(file);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div
        className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          isDragging
            ? "border-instagram-blue bg-instagram-bg"
            : "border-instagram-border bg-white"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".db,.sqlite"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isLoading}
        />

        {isLoading ? (
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto border-4 border-instagram-border border-t-instagram-blue rounded-full animate-spin" />
            <p className="text-instagram-text font-medium">
              Parsing database...
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-instagram-bg flex items-center justify-center">
              <Upload className="w-8 h-8 text-instagram-blue" />
            </div>
            <div>
              <p className="text-lg font-semibold text-instagram-text mb-2">
                Upload your database
              </p>
              <p className="text-sm text-instagram-textSecondary">
                Drag and drop your <code className="bg-instagram-bg px-2 py-1 rounded">instagram_audit.db</code> file here
                <br />
                or click to browse
              </p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-900">Error</p>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
}
