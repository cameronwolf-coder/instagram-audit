"use client";

import { useState } from "react";
import {
  Lock,
  Unlock,
  Users,
  UserPlus,
  UserMinus,
  ArrowLeftRight,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Terminal,
} from "lucide-react";
import { deriveKeyHash, decryptPayload, SyncData } from "../../lib/crypto";

export default function SyncPage() {
  const [passphrase, setPassphrase] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<SyncData | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!passphrase || passphrase.length < 6) {
      setError("Passphrase must be at least 6 characters");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Derive hash for lookup
      const hash = await deriveKeyHash(passphrase);

      // Fetch encrypted data
      const response = await fetch(`/api/sync?hash=${hash}`);

      if (response.status === 404) {
        setError("No data found. Run 'audit sync push' first.");
        setLoading(false);
        return;
      }

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || "Failed to fetch data");
      }

      const encrypted = await response.json();

      // Decrypt client-side
      const decrypted = await decryptPayload(encrypted, passphrase);
      setData(decrypted);
    } catch (err: any) {
      if (err.name === "OperationError") {
        setError("Invalid passphrase. Decryption failed.");
      } else {
        setError(err.message || "Failed to load data");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setData(null);
    setPassphrase("");
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-instagram-secondary via-instagram-primary to-instagram-tertiary">
      <div className="min-h-screen bg-white/90 backdrop-blur-sm">
        {/* Header */}
        <header className="bg-white border-b border-instagram-border shadow-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-instagram-primary to-instagram-secondary flex items-center justify-center">
                  <Lock className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-instagram-text">
                    Cloud Sync
                  </h1>
                  <p className="text-sm text-instagram-textSecondary">
                    View your synced data
                  </p>
                </div>
              </div>
              {data && (
                <button
                  onClick={handleReset}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-instagram-textSecondary hover:text-instagram-text"
                >
                  <RefreshCw className="w-4 h-4" />
                  Change passphrase
                </button>
              )}
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          {!data ? (
            <div className="max-w-md mx-auto">
              {/* Passphrase Form */}
              <div className="bg-white rounded-lg shadow-lg p-8 border border-instagram-border">
                <div className="text-center mb-6">
                  <div className="w-16 h-16 rounded-full bg-instagram-bg flex items-center justify-center mx-auto mb-4">
                    <Unlock className="w-8 h-8 text-instagram-blue" />
                  </div>
                  <h2 className="text-xl font-semibold text-instagram-text mb-2">
                    Enter your passphrase
                  </h2>
                  <p className="text-instagram-textSecondary text-sm">
                    Your data is encrypted. Enter the passphrase you used when
                    syncing.
                  </p>
                </div>

                <form onSubmit={handleSubmit}>
                  <input
                    type="password"
                    value={passphrase}
                    onChange={(e) => setPassphrase(e.target.value)}
                    placeholder="Enter passphrase..."
                    className="w-full px-4 py-3 border border-instagram-border rounded-lg focus:outline-none focus:ring-2 focus:ring-instagram-blue mb-4"
                    disabled={loading}
                  />

                  {error && (
                    <div className="flex items-center gap-2 text-red-600 text-sm mb-4">
                      <AlertCircle className="w-4 h-4" />
                      {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={loading || !passphrase}
                    className="w-full py-3 bg-instagram-blue text-white rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                  >
                    {loading ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Decrypting...
                      </>
                    ) : (
                      <>
                        <Lock className="w-4 h-4" />
                        View Data
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Instructions */}
              <div className="mt-8 bg-instagram-bg rounded-lg p-6 border border-instagram-border">
                <h3 className="font-semibold text-instagram-text mb-3 flex items-center gap-2">
                  <Terminal className="w-4 h-4" />
                  How to sync your data:
                </h3>
                <ol className="space-y-2 text-instagram-textSecondary text-sm">
                  <li className="flex gap-2">
                    <span className="font-medium">1.</span>
                    <span>
                      Install:{" "}
                      <code className="bg-white px-1 rounded">
                        pip install instagram-audit[sync]
                      </code>
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-medium">2.</span>
                    <span>
                      Collect data:{" "}
                      <code className="bg-white px-1 rounded">
                        audit run -i /path/to/export
                      </code>
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="font-medium">3.</span>
                    <span>
                      Sync:{" "}
                      <code className="bg-white px-1 rounded">
                        audit sync push -p "your-passphrase"
                      </code>
                    </span>
                  </li>
                </ol>
              </div>
            </div>
          ) : (
            /* Data Display */
            <div className="max-w-4xl mx-auto">
              {/* Success Banner */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <div>
                  <p className="text-green-800 font-medium">
                    Data decrypted successfully
                  </p>
                  <p className="text-green-600 text-sm">
                    Last synced: {new Date(data.snapshot.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-white rounded-lg p-4 border border-instagram-border text-center">
                  <Users className="w-6 h-6 text-instagram-blue mx-auto mb-2" />
                  <p className="text-2xl font-bold text-instagram-text">
                    {data.snapshot.follower_count.toLocaleString()}
                  </p>
                  <p className="text-sm text-instagram-textSecondary">Followers</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-instagram-border text-center">
                  <UserPlus className="w-6 h-6 text-instagram-blue mx-auto mb-2" />
                  <p className="text-2xl font-bold text-instagram-text">
                    {data.snapshot.following_count.toLocaleString()}
                  </p>
                  <p className="text-sm text-instagram-textSecondary">Following</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-instagram-border text-center">
                  <ArrowLeftRight className="w-6 h-6 text-green-500 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-instagram-text">
                    {data.relationships.mutuals.length.toLocaleString()}
                  </p>
                  <p className="text-sm text-instagram-textSecondary">Mutuals</p>
                </div>
                <div className="bg-white rounded-lg p-4 border border-instagram-border text-center">
                  <UserMinus className="w-6 h-6 text-orange-500 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-instagram-text">
                    {data.relationships.not_followed_back.length.toLocaleString()}
                  </p>
                  <p className="text-sm text-instagram-textSecondary">Not Following Back</p>
                </div>
              </div>

              {/* Changes */}
              {data.diff && (
                <div className="bg-white rounded-lg p-6 border border-instagram-border mb-8">
                  <h3 className="text-lg font-semibold text-instagram-text mb-4">
                    Recent Changes
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <p className="text-xl font-bold text-green-600">
                        +{data.diff.new_followers.length}
                      </p>
                      <p className="text-sm text-instagram-textSecondary">
                        New Followers
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xl font-bold text-red-600">
                        -{data.diff.unfollowers.length}
                      </p>
                      <p className="text-sm text-instagram-textSecondary">
                        Unfollowers
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xl font-bold text-blue-600">
                        +{data.diff.new_following.length}
                      </p>
                      <p className="text-sm text-instagram-textSecondary">
                        New Following
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-xl font-bold text-orange-600">
                        -{data.diff.unfollowing.length}
                      </p>
                      <p className="text-sm text-instagram-textSecondary">
                        Unfollowing
                      </p>
                    </div>
                  </div>

                  {/* Show unfollowers list if any */}
                  {data.diff.unfollowers.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-instagram-border">
                      <p className="text-sm font-medium text-instagram-text mb-2">
                        Unfollowers:
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {data.diff.unfollowers.map((username) => (
                          <a
                            key={username}
                            href={`https://instagram.com/${username}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-2 py-1 bg-red-50 text-red-700 text-sm rounded hover:bg-red-100"
                          >
                            @{username}
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Relationship Lists */}
              <div className="grid md:grid-cols-2 gap-6">
                {/* Not Following Back */}
                <div className="bg-white rounded-lg p-6 border border-instagram-border">
                  <h3 className="text-lg font-semibold text-instagram-text mb-4 flex items-center gap-2">
                    <UserMinus className="w-5 h-5 text-orange-500" />
                    Not Following You Back ({data.relationships.not_followed_back.length})
                  </h3>
                  <div className="max-h-64 overflow-y-auto space-y-1">
                    {data.relationships.not_followed_back.slice(0, 50).map((username) => (
                      <a
                        key={username}
                        href={`https://instagram.com/${username}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block px-2 py-1 text-sm text-instagram-textSecondary hover:bg-instagram-bg rounded"
                      >
                        @{username}
                      </a>
                    ))}
                    {data.relationships.not_followed_back.length > 50 && (
                      <p className="text-sm text-instagram-textSecondary pt-2">
                        +{data.relationships.not_followed_back.length - 50} more
                      </p>
                    )}
                  </div>
                </div>

                {/* You Don't Follow Back */}
                <div className="bg-white rounded-lg p-6 border border-instagram-border">
                  <h3 className="text-lg font-semibold text-instagram-text mb-4 flex items-center gap-2">
                    <Users className="w-5 h-5 text-blue-500" />
                    You Don't Follow Back ({data.relationships.not_following_back.length})
                  </h3>
                  <div className="max-h-64 overflow-y-auto space-y-1">
                    {data.relationships.not_following_back.slice(0, 50).map((username) => (
                      <a
                        key={username}
                        href={`https://instagram.com/${username}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block px-2 py-1 text-sm text-instagram-textSecondary hover:bg-instagram-bg rounded"
                      >
                        @{username}
                      </a>
                    ))}
                    {data.relationships.not_following_back.length > 50 && (
                      <p className="text-sm text-instagram-textSecondary pt-2">
                        +{data.relationships.not_following_back.length - 50} more
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-instagram-border mt-16">
          <div className="container mx-auto px-4 py-8 text-center text-instagram-textSecondary text-sm">
            <p className="mb-2">
              Your data is encrypted client-side. The server cannot read it.
            </p>
            <p>
              <a
                href="/"
                className="text-instagram-blue hover:underline mr-4"
              >
                Upload Database
              </a>
              <a
                href="https://github.com/cameronwolf-coder/instagram-audit"
                target="_blank"
                rel="noopener noreferrer"
                className="text-instagram-blue hover:underline"
              >
                GitHub
              </a>
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
