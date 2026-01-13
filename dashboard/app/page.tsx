"use client";

import { useState } from "react";
import { Upload, Database, TrendingUp, Users, UserCheck } from "lucide-react";
import DatabaseUpload from "@/components/DatabaseUpload";
import Dashboard from "@/components/Dashboard";

export default function Home() {
  const [dbData, setDbData] = useState<any>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-instagram-secondary via-instagram-primary to-instagram-tertiary">
      <div className="min-h-screen bg-white/90 backdrop-blur-sm">
        {/* Header */}
        <header className="bg-white border-b border-instagram-border shadow-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-instagram-primary to-instagram-secondary flex items-center justify-center">
                  <Database className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-instagram-text">
                    Instagram Audit
                  </h1>
                  <p className="text-sm text-instagram-textSecondary">
                    Local-first relationship tracker
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-6 text-sm text-instagram-textSecondary">
                <div className="flex items-center gap-2">
                  <UserCheck className="w-4 h-4" />
                  <span>No login required</span>
                </div>
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4" />
                  <span>100% local data</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="container mx-auto px-4 py-8">
          {!dbData ? (
            <div className="max-w-4xl mx-auto">
              {/* Hero Section */}
              <div className="text-center mb-12">
                <h2 className="text-4xl font-bold text-instagram-text mb-4">
                  Track Your Instagram Relationships
                </h2>
                <p className="text-lg text-instagram-textSecondary mb-8">
                  Upload your local database to visualize followers, following, and changes over time.
                  <br />
                  <span className="text-sm">
                    No Instagram login. No data leaves your browser.
                  </span>
                </p>
              </div>

              {/* Features */}
              <div className="grid md:grid-cols-3 gap-6 mb-12">
                <div className="bg-white rounded-lg p-6 shadow-md border border-instagram-border">
                  <div className="w-12 h-12 rounded-full bg-instagram-bg flex items-center justify-center mb-4">
                    <TrendingUp className="w-6 h-6 text-instagram-blue" />
                  </div>
                  <h3 className="text-lg font-semibold text-instagram-text mb-2">
                    Track Changes
                  </h3>
                  <p className="text-instagram-textSecondary text-sm">
                    See who followed and unfollowed you over time with beautiful visualizations.
                  </p>
                </div>

                <div className="bg-white rounded-lg p-6 shadow-md border border-instagram-border">
                  <div className="w-12 h-12 rounded-full bg-instagram-bg flex items-center justify-center mb-4">
                    <Users className="w-6 h-6 text-instagram-blue" />
                  </div>
                  <h3 className="text-lg font-semibold text-instagram-text mb-2">
                    Relationship Views
                  </h3>
                  <p className="text-instagram-textSecondary text-sm">
                    View mutuals, not-following-back, and not-followed-back lists.
                  </p>
                </div>

                <div className="bg-white rounded-lg p-6 shadow-md border border-instagram-border">
                  <div className="w-12 h-12 rounded-full bg-instagram-bg flex items-center justify-center mb-4">
                    <Database className="w-6 h-6 text-instagram-blue" />
                  </div>
                  <h3 className="text-lg font-semibold text-instagram-text mb-2">
                    100% Private
                  </h3>
                  <p className="text-instagram-textSecondary text-sm">
                    Your data never leaves your browser. Everything is processed locally.
                  </p>
                </div>
              </div>

              {/* Upload Section */}
              <DatabaseUpload onDataLoaded={setDbData} />

              {/* Instructions */}
              <div className="mt-12 bg-instagram-bg rounded-lg p-6 border border-instagram-border">
                <h3 className="text-lg font-semibold text-instagram-text mb-4">
                  How to get your database:
                </h3>
                <ol className="space-y-3 text-instagram-textSecondary">
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-instagram-blue text-white text-sm flex items-center justify-center">
                      1
                    </span>
                    <span>
                      Install the CLI tool: <code className="bg-white px-2 py-1 rounded text-xs">pip install instagram-audit</code>
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-instagram-blue text-white text-sm flex items-center justify-center">
                      2
                    </span>
                    <span>
                      Run: <code className="bg-white px-2 py-1 rounded text-xs">audit run --input /path/to/instagram-export</code>
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-instagram-blue text-white text-sm flex items-center justify-center">
                      3
                    </span>
                    <span>
                      Upload your <code className="bg-white px-2 py-1 rounded text-xs">instagram_audit.db</code> file above
                    </span>
                  </li>
                </ol>
                <div className="mt-4 pt-4 border-t border-instagram-border">
                  <a
                    href="https://github.com/cameronwolf-coder/instagram-audit"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-instagram-blue hover:underline text-sm"
                  >
                    View CLI tool on GitHub →
                  </a>
                </div>
              </div>
            </div>
          ) : (
            <Dashboard data={dbData} onReset={() => setDbData(null)} />
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-instagram-border mt-16">
          <div className="container mx-auto px-4 py-8 text-center text-instagram-textSecondary text-sm">
            <p className="mb-2">
              Built with safety and privacy in mind. No Instagram login required.
            </p>
            <p>
              <a
                href="https://github.com/cameronwolf-coder/instagram-audit"
                target="_blank"
                rel="noopener noreferrer"
                className="text-instagram-blue hover:underline"
              >
                Open Source on GitHub
              </a>
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
